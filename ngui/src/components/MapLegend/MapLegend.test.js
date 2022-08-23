import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MapLegend from "./MapLegend";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MapLegend markers={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
