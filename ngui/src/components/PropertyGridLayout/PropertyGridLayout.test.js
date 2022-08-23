import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PropertyGridLayout from "./PropertyGridLayout";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PropertyGridLayout propertyName={<div />} propertyValue={<div />} iconButtons={<div />} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
