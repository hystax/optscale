import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ShareSettings from "./ShareSettings";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ShareSettings canEdit currentLink={""} onChange={jest.fn} isLoading={false} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
