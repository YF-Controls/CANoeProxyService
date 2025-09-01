from canoe_proxy_tcp_server import CANoeProxyTcpServer


if __name__ == '__main__':

  config_path = r'c:\canoeproxyservice\config.json'
  server = CANoeProxyTcpServer(config_path)
  server.start()

 