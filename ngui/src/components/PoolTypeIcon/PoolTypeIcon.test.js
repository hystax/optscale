import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { POOL_TYPE_BUDGET } from "utils/constants";
import PoolTypeIcon from "./PoolTypeIcon";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PoolTypeIcon type={POOL_TYPE_BUDGET} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
