import React from "react";
import ReactDOM from "react-dom";
import { COLUMNS, RAW_EXPENSES } from "reducers/columns";
import TestProvider from "tests/TestProvider";
import RawExpensesTable from "./RawExpensesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        [COLUMNS]: {
          [RAW_EXPENSES]: []
        }
      }}
    >
      <RawExpensesTable expenses={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
