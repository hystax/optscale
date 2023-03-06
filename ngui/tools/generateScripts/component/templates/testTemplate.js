module.exports = (componentName) => `import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ${componentName} from "./${componentName}";

it("renders without crashing", () => {
  const div = document.createElement("div");
const root = createRoot(div);
  root.render(
    <TestProvider>
      <${componentName} />
    </TestProvider>
  );
  root.unmount();
});
`;
