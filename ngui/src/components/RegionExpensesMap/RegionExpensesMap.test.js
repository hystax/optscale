import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RegionExpensesMap from "./RegionExpensesMap";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RegionExpensesMap markers={[]} defaultCenter={{ lat: 0, lng: 0 }} defaultZoom={1} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
