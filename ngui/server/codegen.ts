import type { CodegenConfig } from "@graphql-codegen/cli";

const commonPlugins = ["typescript", "typescript-resolvers"];

const config: CodegenConfig = {
  overwrite: true,
  generates: {
    "./graphql/resolvers/keeper.generated.ts": {
      schema: "./graphql/schemas/keeper.graphql",
      plugins: commonPlugins,
    },
    "./graphql/resolvers/slacker.generated.ts": {
      schema: "./graphql/schemas/slacker.graphql",
      plugins: commonPlugins,
    },
  },
};

export default config;
