import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MenuItemLoader from "./MenuItemLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MenuItemLoader messageId="name" />,
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
