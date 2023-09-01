FROM redis:7.0.9-alpine

COPY docker_images/redis/redis.conf /etc/redis/redis.conf

CMD [ "redis-server", "/etc/redis/redis.conf" ]