import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import FormButtonsWrapper from "./FormButtonsWrapper";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <FormButtonsWrapper>
        <div>child</div>
      </FormButtonsWrapper>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
