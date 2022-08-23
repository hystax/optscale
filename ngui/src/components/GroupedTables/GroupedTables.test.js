import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import GroupedTables from "./GroupedTables";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <GroupedTables
        groupedResources={[
          [
            "groupValue",
            {
              displayedGroupName: "displayedGroupName",
              count: 0,
              totalExpenses: 0,
              expenses: []
            }
          ]
        ]}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
