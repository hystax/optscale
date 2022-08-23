import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PageContentWrapper from "./PageContentWrapper";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PageContentWrapper>Content</PageContentWrapper>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
