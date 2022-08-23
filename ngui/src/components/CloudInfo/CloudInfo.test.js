import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { AWS_CNR } from "utils/constants";
import CloudInfo from "./CloudInfo";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CloudInfo type={AWS_CNR} lastImportAt={0} config={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
