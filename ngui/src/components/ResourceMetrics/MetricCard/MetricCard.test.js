import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MetricCard from "./MetricCard";

it("renders empty message without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MetricCard title="title" cardBodyDefinition={{ emptyMessage: "message" }} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

it("renders chart without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MetricCard title="title" cardBodyDefinition={{ chartProps: { lines: [] } }} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
