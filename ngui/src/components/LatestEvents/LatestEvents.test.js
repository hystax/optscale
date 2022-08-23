import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import LatestEvents from "./LatestEvents";

it("renders without crashing with 0 events", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <LatestEvents count={0} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

it("renders without crashing with 1 event", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <LatestEvents count={1} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
