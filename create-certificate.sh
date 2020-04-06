openssl req -sha256 -newkey rsa:2048 -nodes -keyout ./Proxy/ssl_key.pem -x509 -days 730 -out ./Proxy/ssl_cert.pem -config cert-config.conf -extensions 'v3_req'
