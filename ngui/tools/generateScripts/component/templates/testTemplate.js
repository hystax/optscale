module.exports = (componentName) => `import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ${componentName} from "./${componentName}";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <${componentName} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
`;
