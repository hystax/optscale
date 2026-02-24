import hystaxConfig from "@hystax/eslint-config-ui";
import reactPlugin from "eslint-plugin-react";

export default [
  hystaxConfig,
  {
    rules: { "react/jsx-curly-brace-presence": ["error", { props: "never", children: "never" }] },
    ignores: [],
    settings: {},
    languageOptions: {},
    plugins: { react: reactPlugin },
  }, // custom rules can be added here
];
