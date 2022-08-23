import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import OrganizationSelector from "./OrganizationSelector";

const pools = [
  {
    deleted_at: 0,
    id: "a2e75d53-4a90-4f28-9a97-dead860b3d58",
    created_at: null,
    name: "Partner",
    parent_id: null
  }
];

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <OrganizationSelector pools={pools} organizationId={pools[0].id} onChange={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
