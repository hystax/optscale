ARG IMAGE=node:16.15.0-alpine3.14

FROM $IMAGE

WORKDIR /src

COPY .env server.js jsconfig.json package.json package-lock.json scripts/prune_node_modules.sh ./
COPY .storybook .storybook/
COPY public public/
COPY src src/

RUN npm ci --production --ignore-scripts
RUN ./prune_node_modules.sh
RUN npm run build && npm run storybook:build


FROM $IMAGE

WORKDIR /src

COPY --from=0 /src/build ./build
COPY --from=0 /src/node_modules ./node_modules
COPY --from=0 /src/storybook ./storybook
COPY --from=0 /src/package.json /src/server.js ./

CMD ["npm", "run", "server"]
