import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EnvironmentPropertyValueInput from "./EnvironmentPropertyValueInput";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EnvironmentPropertyValueInput name="name" register={jest.fn} />
    </TestProvider>
  );
  root.unmount();
});
