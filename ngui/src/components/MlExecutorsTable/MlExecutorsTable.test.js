import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MlExecutorsTable from "./MlExecutorsTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MlExecutorsTable executors={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
