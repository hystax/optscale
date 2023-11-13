// https://eslint.org/docs/latest/use/configure/#configuration-file-formats
module.exports = {
  parser: "@typescript-eslint/parser",
  globals: {
    Atomics: "readonly",
    SharedArrayBuffer: "readonly",
    globalThis: "readonly",
    // Allow using «vi» in tests without warnings
    vi: true
  },
  parserOptions: {
    ecmaVersion: 2024,
    sourceType: "module",
    ecmaFeatures: {
      jsx: true
    }
  },
  settings: {
    "import/resolver": {
      node: {
        extensions: [".js", ".jsx", ".ts", ".tsx"],
        moduleDirectory: ["node_modules", "src/"]
      }
    },
    react: {
      version: "detect"
    }
  },
  env: {
    browser: true,
    es6: true,
    node: true,
    jest: true
  },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "airbnb-base",
    "prettier"
  ],
  plugins: ["react", "react-hooks", "unused-imports"],
  rules: {
    "no-console": "off",
    "jsx-quotes": 1,
    "react/no-typos": 1,
    "no-multi-spaces": 1,
    "react/jsx-tag-spacing": 1,
    "react/jsx-boolean-value": 1,
    "react/no-array-index-key": 1,
    "react/jsx-wrap-multilines": 1,
    "react/self-closing-comp": 1,
    "react/jsx-closing-bracket-location": 1,
    "react/require-render-return": 1,
    "react/jsx-uses-react": 1,
    "react/jsx-uses-vars": [2],
    "react/no-multi-comp": 0,
    "react/display-name": 0,
    "react/prefer-es6-class": 1,
    "react/prefer-stateless-function": 1,
    "react/prop-types": [2, { skipUndeclared: true }],
    "react-hooks/exhaustive-deps": "warn",
    "react-hooks/rules-of-hooks": "error",
    "import/no-extraneous-dependencies": 0,
    "import/prefer-default-export": 0,
    // TS migration new rules
    "import/extensions": 0,
    "@typescript-eslint/ban-ts-comment": 0,
    "@typescript-eslint/no-empty-function": 0,
    "react/react-in-jsx-scope": 0,
    "@typescript-eslint/no-unused-vars": 0,
    // -----------------------
    "no-const-assign": "warn",
    "no-underscore-dangle": [
      "error",
      {
        allowAfterThis: true,
        allowAfterThisConstructor: true
      }
    ],
    "no-this-before-super": "warn",
    "no-undef": "warn",
    "no-unreachable": "warn",
    "no-unused-vars": "warn",
    "unused-imports/no-unused-imports": "warn",
    "arrow-body-style": "warn",
    "import/order": [
      "warn",
      {
        groups: ["builtin", "external", "internal", "parent", "sibling", "index"],
        pathGroups: [
          {
            pattern: "react",
            group: "builtin",
            position: "before"
          }
        ],
        pathGroupsExcludedImportTypes: ["react"],
        alphabetize: {
          order: "asc",
          caseInsensitive: true
        }
      }
    ],
    "no-bitwise": 0,
    "constructor-super": "warn",
    "valid-typeof": "warn",
    "no-extra-semi": "warn",
    "comma-dangle": [
      "warn",
      {
        arrays: "never",
        objects: "never"
      }
    ],
    "max-params": ["warn", 3],
    "default-param-last": 0
  }
};
