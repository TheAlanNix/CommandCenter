FROM nginx

COPY .htpasswd /etc/nginx/.htpasswd
COPY default.conf /etc/nginx/conf.d
COPY ssl_cert.pem /etc/nginx/ssl_cert.pem
COPY ssl_key.pem /etc/nginx/ssl_key.pem
