from canoe_proxy_tcp_server import CANoeProxyTcpServer


if __name__ == '__main__':

  config_path = r'c:\canoeproxy\config.json'
  server = CANoeProxyTcpServer(config_path)
  server.start()

 