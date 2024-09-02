import type { CodegenConfig } from "@graphql-codegen/cli";
import { JSONObjectResolver } from "graphql-scalars";

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
    "./graphql/resolvers/restapi.generated.ts": {
      schema: "./graphql/schemas/restapi.graphql",
      plugins: commonPlugins,
      config: {
        scalars: {
          JSONObject: JSONObjectResolver.extensions.codegenScalarType,
        },
      },
    },
  },
};

export default config;
