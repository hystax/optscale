import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EnvironmentsTable from "./EnvironmentsTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EnvironmentsTable data={[]} onUpdateActivity={() => {}} entityId="123" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
