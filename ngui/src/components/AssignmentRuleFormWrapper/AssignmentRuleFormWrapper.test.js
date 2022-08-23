import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import AssignmentRuleFormWrapper from "./AssignmentRuleFormWrapper";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <AssignmentRuleFormWrapper
        cloudAccounts={[]}
        pools={[]}
        onSubmit={jest.fn}
        onCancel={jest.fn}
        onPoolChange={jest.fn}
        poolOwners={[]}
        isFormDataLoading={false}
        isSubmitLoading={false}
        defaultValues={{
          name: "",
          active: false,
          conditions: [],
          poolId: "",
          ownerId: ""
        }}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
