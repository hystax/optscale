# -------- Setup --------
ARG IMAGE=node:18.14.2-alpine3.16

FROM $IMAGE as builder

WORKDIR /usr/src/app

ENV NODE_ENV production

# -------- UI --------
WORKDIR /usr/src/app/ui
COPY ngui/ui/package*.json ./
RUN npm ci --ignore-scripts
COPY ngui/ui/ ./
# .eslintrc.js on build step will produce an error, but it is still needed on testing
RUN mv .eslintrc.js .disabled.eslintrc.js
RUN npm run build && rm -rf node_modules

# -------- Server --------
WORKDIR /usr/src/app/server
COPY ngui/server/package*.json ./
RUN npm ci --ignore-scripts
COPY ngui/server/ ./
RUN ./scripts/prune_node_modules.sh
RUN npm run compile
RUN chown -R node:node /usr/src/app/

# -------- Final stage --------
FROM $IMAGE

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/ui/ ./ui
COPY --from=builder /usr/src/app/server ./server

EXPOSE 4000

# generate environment variables and run the server
USER node
WORKDIR /usr/src/app/server
COPY --from=builder /usr/src/app/ui/prepare-and-run.sh /
RUN chmod +x /prepare-and-run.sh

CMD [ "/prepare-and-run.sh" ]