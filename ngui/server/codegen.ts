import type { CodegenConfig } from "@graphql-codegen/cli";

const config: CodegenConfig = {
  overwrite: true,
  schema: [
    "./graphql/schemas/keeper.graphql",
    "./graphql/schemas/slacker.graphql",
  ],
  generates: {
    "./graphql/__generated__/resolversTypes.ts": {
      plugins: ["typescript", "typescript-resolvers"],
    },
  },
};

export default config;
