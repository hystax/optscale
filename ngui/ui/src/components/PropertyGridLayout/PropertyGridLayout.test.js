import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PropertyGridLayout from "./PropertyGridLayout";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PropertyGridLayout propertyName={<div />} propertyValue={<div />} iconButtons={<div />} />
    </TestProvider>
  );
  root.unmount();
});
