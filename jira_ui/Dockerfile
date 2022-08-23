ARG IMAGE=node:14.16.0-alpine3.13

# -------------------------

FROM $IMAGE

WORKDIR /src

RUN apk update && \
  apk upgrade && \
  apk --no-cache add curl

COPY config.js server.js package.json package-lock.json jsconfig.json ./
COPY public public/
COPY src src/

RUN npm ci --only=production --ignore-scripts && npm run build

RUN curl -sfL https://gobinaries.com/tj/node-prune | sh && \
  /usr/local/bin/node-prune

# -------------------------

FROM $IMAGE

WORKDIR /src

COPY --from=0 /src/build ./build
COPY --from=0 /src/node_modules ./node_modules
COPY --from=0 /src/package.json /src/server.js /src/config.js ./

ENV REACT_APP_ENV=docker

CMD ["npm", "run", "server"]
