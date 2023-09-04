# -------- Setup --------
ARG IMAGE=node:14.16.0-alpine3.13

FROM $IMAGE as builder

WORKDIR /usr/src/app

ENV NODE_ENV production

# -------- UI --------
WORKDIR /usr/src/app/ui
COPY jira_ui/ui/package*.json ./
RUN npm ci --ignore-scripts
COPY jira_ui/ui/ ./
# .eslintrc.json on build step will produce an error, but it is still needed on testing
RUN mv .eslintrc.json .disabled.eslintrc.json
RUN npm run build && rm -rf node_modules

# -------- Server --------
WORKDIR /usr/src/app/server
COPY jira_ui/server/package*.json ./
RUN npm ci --ignore-scripts
COPY jira_ui/server/ ./
RUN ./scripts/prune_node_modules.sh

# -------- Final stage --------
FROM $IMAGE

WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/ui/ ./ui
COPY --from=builder /usr/src/app/server ./server

EXPOSE 4000

WORKDIR /usr/src/app/server

CMD ["npm", "start"]
