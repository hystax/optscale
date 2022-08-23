import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ConnectSlack from "./ConnectSlack";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ConnectSlack isLoading />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
