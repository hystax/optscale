import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Greeter from "./Greeter";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Greeter form={<div>Form</div>} />
    </TestProvider>
  );
  root.unmount();
});
