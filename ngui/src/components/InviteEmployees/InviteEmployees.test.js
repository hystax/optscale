import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import InviteEmployees from "./InviteEmployees";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <InviteEmployees isLoadingProps={false} onSubmit={jest.fn} availablePools={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
