import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CloudExpensesChartMarker from "./CloudExpensesChartMarker";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CloudExpensesChartMarker value={100} valueMessageId="pool" chartBase={100} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
