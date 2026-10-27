import hystaxConfig from "@hystax/eslint-config-ui";
import reactPlugin from "eslint-plugin-react";

export default [
  ...hystaxConfig,
  {
    files: ["**/graphql/__generated__/**"],
    rules: {
      "no-redeclare": "off",
    },
  },
  // Temporary rule to avoid warnings during checks with eslint-config-ui@2.1.0
  {
    files: ["**/BookingsCalendar.tsx", "**/datetime.ts"],
    rules: { "import/no-duplicates": "off" },
  },
  // custom rules can be added here
];
