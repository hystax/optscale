import React from "react";
import ErrorIcon from "@mui/icons-material/Error";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Icon from "./Icon";

it("renders without crashing without children", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Icon icon={ErrorIcon} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
