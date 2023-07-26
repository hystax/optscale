# -------- Setup --------
ARG IMAGE=node:18.14.2-alpine3.16

FROM $IMAGE as builder

WORKDIR /usr/src/app

ENV NODE_ENV production

# -------- UI --------
WORKDIR /usr/src/app/ui
COPY ui/package*.json ./
RUN npm ci --ignore-scripts
COPY ui/ ./
RUN npm run build && rm -rf node_modules

# -------- Server --------
WORKDIR /usr/src/app/server
COPY server/package*.json ./
RUN npm ci --ignore-scripts
COPY server/ ./
RUN ./scripts/prune_node_modules.sh
RUN npm run compile

# -------- Final stage --------
FROM $IMAGE

WORKDIR /usr/src/app

RUN chown node:node ./
USER node

COPY --from=builder /usr/src/app/ui/ ./ui
COPY --from=builder /usr/src/app/server ./server

EXPOSE 4000

WORKDIR /usr/src/app/server

CMD ["node", "./dist/server.js"]