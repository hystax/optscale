import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EditOrganizationConstraintNameForm from "./EditOrganizationConstraintNameForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EditOrganizationConstraintNameForm defaultName="" onCancel={jest.fn} onSubmit={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
