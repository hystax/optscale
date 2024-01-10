FROM sebp/elk:7.16.2

RUN apt-get update \
    && apt-get install apache2-utils -y \
    && apt-get install -y nginx \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm /etc/nginx/sites-enabled/default

RUN /opt/logstash/bin/logstash-plugin install logstash-input-gelf

EXPOSE 12201/udp
EXPOSE 80

VOLUME /var/lib/elasticsearch/

COPY docker_images/elk/40-logstash-gelp.conf docker_images/elk/50-ruby-filter.conf /etc/logstash/conf.d/
COPY docker_images/elk/kibana.yml /opt/kibana/config/

COPY docker_images/elk/kibana-proxy /etc/nginx/sites-available/
COPY docker_images/elk/kibana-proxy /etc/nginx/sites-enabled/
COPY docker_images/elk/generate_htpasswd.sh /

CMD ["bash", "-c", "/generate_htpasswd.sh && service nginx start && /usr/local/bin/start.sh"]
