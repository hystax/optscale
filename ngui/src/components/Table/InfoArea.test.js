import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import InfoArea from "./InfoArea";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <InfoArea selectedRowsCount={10} showCounters hideTotal={false} totalNumber={5050} rowsLength={20} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
