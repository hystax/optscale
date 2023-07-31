import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EnvironmentProperty from "./EnvironmentProperty";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EnvironmentProperty environmentId="" propertyName="" propertyValue="" existingProperties={{}} />
    </TestProvider>
  );
  root.unmount();
});
