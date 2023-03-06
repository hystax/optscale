ARG IMAGE=node:18.12.1-alpine3.15

FROM $IMAGE

WORKDIR /src

COPY .env server.js jsconfig.json package.json package-lock.json scripts/prune_node_modules.sh ./
COPY public public/
COPY src src/

RUN npm ci --production --ignore-scripts --legacy-peer-deps
RUN ./prune_node_modules.sh
RUN npm run build

FROM $IMAGE

WORKDIR /src

COPY --from=0 /src/build ./build
COPY --from=0 /src/node_modules ./node_modules
COPY --from=0 /src/package.json /src/server.js ./

CMD ["npm", "run", "server"]
