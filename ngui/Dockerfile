# --- Base Stage ---
ARG IMAGE=node:22.16.0-alpine3.21

FROM $IMAGE AS base

RUN npm install -g pnpm@10.33.0
  
ENV NODE_ENV production

# --- Setup project source stage ---
FROM base AS source

WORKDIR /usr/src/app

COPY ngui/ .

RUN pnpm install --frozen-lockfile --ignore-scripts

# --- Build stage ---
FROM source AS builder

WORKDIR /usr/src/app

RUN pnpm run -r build
  
# Prepare production dependencies for the server
RUN pnpm deploy --filter=server --prod ./prod/server && \
    ./prod/server/scripts/prune_node_modules.sh

# Remove UI node_modules to save space
# The UI will be served statically
RUN rm -rf ./ui/node_modules

# --- Production Stage ---
FROM base AS production

WORKDIR /usr/src/app

# server
COPY --from=builder /usr/src/app/prod/server/dist ./server/dist
COPY --from=builder /usr/src/app/prod/server/node_modules ./server/node_modules

# ui
COPY --from=builder /usr/src/app/ui/build ./ui/build

# prepare-and-run.sh
COPY --from=builder /usr/src/app/prepare-and-run.sh ./prepare-and-run.sh

RUN chmod +x ./prepare-and-run.sh

EXPOSE 4000

CMD ["./prepare-and-run.sh"]