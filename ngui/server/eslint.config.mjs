import nodePlugin from "eslint-plugin-node";
import eslintPluginImport from "eslint-plugin-import";
import eslintPluginPrettier from "eslint-plugin-prettier";
import typescriptPlugin from "@typescript-eslint/eslint-plugin";
import typescriptParser from "@typescript-eslint/parser";
import graphqlPlugin from "@graphql-eslint/eslint-plugin";
import js from "@eslint/js";

export default [
  {
    ignores: ["**/node_modules/**", "**/dist/**", "**/build/**", "**/graphql/__generated__/**", "**/graphql/typeDefs/root.ts"]
  },
  {
    files: ["**/*.ts"],
    ignores: ["**/graphql/__generated__/**"],
    processor: graphqlPlugin.processor,
    plugins: {
      node: nodePlugin,
      import: eslintPluginImport,
      "@typescript-eslint": typescriptPlugin,
      prettier: eslintPluginPrettier
    },
    languageOptions: {
      parser: typescriptParser,
      parserOptions: { ecmaVersion: "latest", sourceType: "module" },
      globals: { process: "readonly", __dirname: "readonly", console: "readonly", URLSearchParams: "readonly" }
    },
    rules: {
      ...js.configs.recommended.rules,
      ...typescriptPlugin.configs.recommended.rules,

      "node/no-missing-import": "off",
      "node/no-unsupported-features/es-syntax": "off",

      "@typescript-eslint/no-unused-vars": ["warn", { ignoreRestSiblings: true }],
      "@typescript-eslint/no-empty-function": "off",
      "@typescript-eslint/no-use-before-define": ["error", { functions: true, classes: true, variables: true }],
      "no-shadow": "off",
      "@typescript-eslint/no-shadow": ["error", { hoist: "functions", allow: [] }],

      ...eslintPluginImport.flatConfigs.recommended.rules,
      "import/no-unresolved": "off",
      "import/order": [
        "warn",
        { groups: ["builtin", "external", "internal", "parent", "sibling", "index"], "newlines-between": "never" }
      ],

      "prettier/prettier": "error"
    }
  },
  {
    files: ["**/*.graphql"],
    ignores: ["**/node_modules/**", "**/dist/**", "**/build/**", "**/graphql/__generated__/**"],
    languageOptions: { parser: graphqlPlugin.parser },
    plugins: { "@graphql-eslint": graphqlPlugin },
    rules: {
      ...graphqlPlugin.configs["flat/schema-recommended"].rules,

      "@graphql-eslint/strict-id-in-types": "off",
      "@graphql-eslint/require-description": "off",
      "@graphql-eslint/no-hashtag-description": "off",
      "@graphql-eslint/no-typename-prefix": "off",
      "@graphql-eslint/naming-convention": [
        "error",
        {
          OperationDefinition: {
            style: "PascalCase",
            forbiddenPrefixes: ["Query", "Mutation", "Subscription", "Get"],
            forbiddenSuffixes: ["Query", "Mutation", "Subscription"]
          },
          EnumTypeDefinition: { style: "PascalCase" },
          "FieldDefinition[parent.name.value=Query]": { style: "camelCase" },
          "FieldDefinition[parent.name.value=Mutation]": { style: "camelCase" },
          "FieldDefinition:not([parent.name.value=Query]):not([parent.name.value=Mutation])": { style: "snake_case" }
        }
      ]
    }
  }
];