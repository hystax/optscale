# -------- Setup --------
ARG IMAGE=node:20.10.0-alpine3.18

FROM $IMAGE as builder

WORKDIR /usr/src/app

ENV NODE_ENV production

RUN npm install -g pnpm@8.11.0

# -------- UI --------
WORKDIR /usr/src/app/ui
COPY ngui/ui/package.json ./package.json
COPY ngui/ui/pnpm-lock.yaml ./pnpm-lock.yaml
RUN pnpm install --frozen-lockfile --ignore-scripts
COPY ngui/ui/ ./
# .eslintrc.js on build step will produce an error, but it is still needed on testing
RUN mv .eslintrc.js .disabled.eslintrc.js
RUN pnpm build && rm -rf node_modules

# -------- Server --------
WORKDIR /usr/src/app/server
COPY ngui/server/package.json ./package.json
COPY ngui/server/pnpm-lock.yaml ./pnpm-lock.yaml
RUN pnpm install --frozen-lockfile --ignore-scripts
COPY ngui/server/ ./
RUN ./scripts/prune_node_modules.sh
RUN pnpm compile
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