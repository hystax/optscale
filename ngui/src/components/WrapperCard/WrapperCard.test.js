import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import WrapperCard from "./WrapperCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <WrapperCard />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
