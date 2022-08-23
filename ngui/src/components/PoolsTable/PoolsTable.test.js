import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PoolsTable from "./PoolsTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PoolsTable
        poolId="random-unit-id"
        rootPool={{ id: "random-unit-id", children: [] }}
        isLoadingProps={{ isGetPoolLoading: false, isGetPoolAllowedActionsLoading: false }}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
