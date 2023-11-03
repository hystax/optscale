import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PropertyLayout from "./PropertyLayout";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PropertyLayout propertyName={<div />} propertyValue={<div />} iconButtons={<div />} />
    </TestProvider>
  );
  root.unmount();
});
