import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TabsLoader from "./TabsLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TabsLoader tabsCount={1} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
