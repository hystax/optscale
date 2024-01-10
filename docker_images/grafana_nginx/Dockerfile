FROM nginx:1.25.3

RUN apt-get update && apt-get install apache2-utils -y
COPY docker_images/grafana_nginx/grafana-proxy /etc/nginx/conf.d/default.conf
COPY docker_images/grafana_nginx/generate_htpasswd.sh /

CMD ["bash", "-c", "/generate_htpasswd.sh && nginx -g 'daemon off;'"]
