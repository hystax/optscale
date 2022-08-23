import React from "react";
import ReactDOM from "react-dom";
import { LATEST_SUCCESS_HANDLED_LABEL } from "api/reducer";
import TestProvider from "tests/TestProvider";
import ApiSuccessAlert from "./ApiSuccessAlert";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        api: { [LATEST_SUCCESS_HANDLED_LABEL]: "" }
      }}
    >
      <ApiSuccessAlert />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
