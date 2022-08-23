import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CreateOrganizationConstraintForm from "./CreateOrganizationConstraintForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CreateOrganizationConstraintForm onSubmit={jest.fn} types={[]} navigateAway={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
