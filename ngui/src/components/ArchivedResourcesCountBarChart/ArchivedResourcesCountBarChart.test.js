import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ArchivedResourcesCountBarChart from "./ArchivedResourcesCountBarChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ArchivedResourcesCountBarChart onSelect={jest.fn} breakdown={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
