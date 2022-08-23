import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TagsBreakdownTable from "./TagsBreakdownTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TagsBreakdownTable data={[]} appliedRange={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
