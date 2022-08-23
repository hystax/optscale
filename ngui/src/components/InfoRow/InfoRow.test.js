import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import InfoRow from "./InfoRow";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <InfoRow title={"test title"} value={"test value"} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
