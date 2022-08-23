import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RightsizingFlavorCell from "./RightsizingFlavorCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RightsizingFlavorCell flavorName="name" flavorCpu={1} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
