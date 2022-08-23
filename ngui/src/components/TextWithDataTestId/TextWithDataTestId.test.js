import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TextWithDataTestId from "./TextWithDataTestId";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TextWithDataTestId dataTestId="test">test</TextWithDataTestId>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
