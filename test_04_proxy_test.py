#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import queue
import socket
import threading
from typing import Optional, Tuple

class TcpProxyServer:
  """
  Servidor proxy TCP orientado a comandos.

  Protocolo (línea por línea, UTF-8) entre cliente <-> proxy:
    connect <ip> <port>
    disconnect <ip> <port>
    status
    command <timeout_sec> <subcommand> <subargument...>
  """

  def __init__(self, host: str = "0.0.0.0", port: int = 9000, backlog: int = 100):
    self.host = host
    self.port = port
    self.backlog = backlog
    self._lsock: Optional[socket.socket] = None
    self._stop_event = threading.Event()
    self._threads = []

    # Logger interno de la clase
    self.log = logging.getLogger(self.__class__.__name__)
    if not self.log.handlers:
      self.log.setLevel(logging.INFO)
      h = logging.StreamHandler()
      fmt = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
      h.setFormatter(logging.Formatter(fmt))
      self.log.addHandler(h)

  # ---------------------- Ciclo de vida del servidor ----------------------

  def start(self):
    self._lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._lsock.bind((self.host, self.port))
    self._lsock.listen(self.backlog)
    self.log.info(f"Proxy escuchando en {self.host}:{self.port}")

    try:
      while not self._stop_event.is_set():
        try:
          self._lsock.settimeout(1.0)
          client_socket, client_address = self._lsock.accept()
        except socket.timeout:
          continue
        t = threading.Thread(target=self._handle_client, args=(client_socket, client_address), daemon=True)
        t.start()
        self._threads.append(t)
        self.log.info(f"Cliente conectado desde {client_address[0]}:{client_address[1]}")
    finally:
      self.stop()

  def stop(self):
    self._stop_event.set()
    if self._lsock:
      try:
        self._lsock.close()
      except Exception:
        pass
      self._lsock = None
    for t in list(self._threads):
      if t.is_alive():
        t.join(timeout=0.1)
    self.log.info("Proxy detenido")

  # ---------------------- Worker de conexión remota ----------------------

  class _RemoteWorker:
    def __init__(self, logger: logging.Logger, raddr: Tuple[str, int], sock: socket.socket):
      self.log = logger
      self.raddr = raddr
      self.sock = sock
      self.req_q: "queue.Queue[dict]" = queue.Queue()
      self._alive = threading.Event()
      self._alive.set()
      self._thr = threading.Thread(target=self._run, daemon=True)
      self._lock = threading.Lock()

    def start(self):
      self._thr.start()

    def stop(self):
      self._alive.clear()
      try:
        with self._lock:
          try:
            self.sock.shutdown(socket.SHUT_RDWR)
          except Exception:
            pass
          self.sock.close()
      except Exception:
        pass
      # Vaciar cola y liberar a quien espere
      while True:
        try:
          item = self.req_q.get_nowait()
        except queue.Empty:
          break
        try:
          item["event"].set()
        except Exception:
          pass
      if self._thr.is_alive():
        self._thr.join(timeout=0.5)

    def request(self, payload: bytes, timeout: float):
      import threading as _th
      ev = _th.Event()
      res = {"ok": False, "data": b"", "err": None}
      self.req_q.put({
        "payload": payload,
        "timeout": float(timeout),
        "event": ev,
        "result": res,
      })
      ev.wait(timeout=float(timeout) + 1.0)
      return res["ok"], res["data"], res["err"]

    def _run(self):
      self.log.debug(f"RemoteWorker iniciado para {self.raddr[0]}:{self.raddr[1]}")
      while self._alive.is_set():
        try:
          item = self.req_q.get(timeout=0.2)
        except queue.Empty:
          continue

        payload: bytes = item["payload"]
        timeout: float = item["timeout"]
        res = item["result"]
        ev = item["event"]

        try:
          with self._lock:
            # Enviar
            self.sock.sendall(payload)
            # Primer recv: timeout del usuario
            self.sock.settimeout(max(0.0, timeout))
            data_chunks = []
            try:
              chunk = self.sock.recv(65536)
              if chunk:
                data_chunks.append(chunk)
            except socket.timeout:
              pass
            # Lecturas breves para drenar resto
            self.sock.settimeout(0.2)
            while True:
              try:
                chunk = self.sock.recv(65536)
                if not chunk:
                  break
                data_chunks.append(chunk)
              except socket.timeout:
                break

            res["ok"] = True
            res["data"] = b"".join(data_chunks)
            res["err"] = None
        except Exception as e:
          res["ok"] = False
          res["data"] = b""
          res["err"] = f"{type(e).__name__}: {e}"
          self.log.warning(f"Error en RemoteWorker {self.raddr}: {e}")
        finally:
          ev.set()
      self.log.debug(f"RemoteWorker detenido para {self.raddr[0]}:{self.raddr[1]}")

  # ---------------------- Manejo de cliente ----------------------

  def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
    # Estado por cliente
    remote_worker: Optional[TcpProxyServer._RemoteWorker] = None
    remote_addr: Optional[Tuple[str, int]] = None

    # Mejor interactividad en algunos clientes
    try:
      client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except Exception:
      pass

    def send_line(s: str):
      try:
        client_socket.sendall((s + "\n").encode("utf-8", errors="replace"))
      except Exception:
        pass

    # Importante: newline=None => modo universal (\n, \r\n, \r)
    #f = client_socket.makefile("r", encoding="utf-8", errors="replace", newline=None)

    try:
      send_line("OK TcpProxyServer listo")
      while True:
        try:
          #line = f.readline()
          line = client_socket.recv(1024).decode('utf-8')
          
        except Exception as e:
          self.log.debug(f"readline() falló para {client_address}: {e}")
          break

        if not line:
          # EOF del cliente
          break

        line = line.strip()
        if not line:
          continue

        parts = line.split()
        cmd = parts[0].lower()

        try:
          if cmd == "connect":
            
            if len(parts) != 3:
              send_line("ERR uso: connect <ip> <port>")
              continue
            ip = parts[1]
            try:
              port = int(parts[2])
            except ValueError:
              send_line("ERR puerto inválido")
              continue

            if remote_worker is not None and remote_addr == (ip, port):
              send_line(f"OK ya conectado a {ip}:{port}")
              continue

            if remote_worker is not None:
              self._close_remote(remote_worker)
              remote_worker = None
              remote_addr = None

            try:
              rsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              rsock.settimeout(5.0)
              rsock.connect((ip, port))
              remote_worker = self._RemoteWorker(self.log, (ip, port), rsock)
              remote_worker.start()
              remote_addr = (ip, port)
              send_line(f"OK conectado a {ip}:{port}")
              self.log.info(f"Cliente {client_address} conectado remotamente a {ip}:{port}")
            except Exception as e:
              try:
                rsock.close()
              except Exception:
                pass
              send_line(f"ERR no se pudo conectar: {type(e).__name__}: {e}")

          elif cmd == "disconnect":
            if len(parts) != 3:
              send_line("ERR uso: disconnect <ip> <port>")
              continue
            ip = parts[1]
            try:
              port = int(parts[2])
            except ValueError:
              send_line("ERR puerto inválido")
              continue

            if remote_worker is None or remote_addr != (ip, port):
              send_line("ERR no conectado a ese destino")
              continue

            self._close_remote(remote_worker)
            remote_worker = None
            remote_addr = None
            send_line(f"OK desconectado de {ip}:{port}")
            self.log.info(f"Cliente {client_address} desconectado de {ip}:{port}")

          elif cmd == "status":
            if remote_worker is not None and remote_addr is not None:
              send_line(f"OK conectado {remote_addr[0]} {remote_addr[1]}")
            else:
              send_line("OK desconectado")

          elif cmd == "command":
            if remote_worker is None or remote_addr is None:
              send_line("ERR no hay conexión remota activa")
              continue
            if len(parts) < 3:
              send_line("ERR uso: command <timeout_sec> <subcommand> <subargument...>")
              continue
            try:
              timeout = float(parts[1])
              if timeout <= 0.0:
                raise ValueError("timeout <= 0.0")
            except Exception:
              send_line("ERR timeout inválido")
              continue

            subcommand = parts[2]
            subargument = " ".join(parts[3:]) if len(parts) > 3 else ""
            outgoing = (subcommand + (" " + subargument if subargument else "")).encode("utf-8", errors="replace")

            ok, data, err = remote_worker.request(outgoing, timeout)
            if not ok:
              send_line(f"ERR fallo al enviar/recibir: {err}")
            else:
              try:
                txt = data.decode("utf-8")
                #send_line("OK RESPONSE BEGIN")
                for ln in txt.splitlines():
                  send_line(ln)
                #send_line("OK RESPONSE END")
                
              except UnicodeDecodeError:
                #send_line("OK RESPONSE BEGIN (hex)")
                send_line(data.hex())
                #send_line("OK RESPONSE END")

          else:
            send_line("ERR comando no reconocido")
        except Exception as e:
          # No matar el hilo del cliente por un error de comando
          self.log.warning(f"Error procesando comando '{line}' de {client_address}: {e}")
          send_line(f"ERR excepción: {type(e).__name__}: {e}")
    finally:
      #try:
      #  f.close()
      #except Exception:
      #  pass
      try:
        client_socket.close()
      except Exception:
        pass
      if remote_worker is not None:
        self._close_remote(remote_worker)
      self.log.info(f"Cliente desconectado {client_address[0]}:{client_address[1]}")

  @staticmethod
  def _close_remote(worker: "_RemoteWorker"):
    try:
      worker.stop()
    except Exception:
      pass

def main():
  parser = argparse.ArgumentParser(description="TcpProxyServer - Proxy TCP basado en comandos")
  parser.add_argument("--host", default="0.0.0.0", help="Host de escucha (por defecto: 0.0.0.0)")
  parser.add_argument("--port", type=int, default=9000, help="Puerto de escucha (por defecto: 9000)")
  parser.add_argument("--log", default="INFO", help="Nivel de log (DEBUG, INFO, WARNING, ERROR)")
  args = parser.parse_args()

  logging.basicConfig(level=getattr(logging, args.log.upper(), logging.INFO))

  srv = TcpProxyServer(host=args.host, port=args.port)
  try:
    srv.start()
  except KeyboardInterrupt:
    pass
  finally:
    srv.stop()

if __name__ == "__main__":
  main()
