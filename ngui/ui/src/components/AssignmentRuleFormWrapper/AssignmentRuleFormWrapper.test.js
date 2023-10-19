import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import AssignmentRuleFormWrapper from "./AssignmentRuleFormWrapper";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <AssignmentRuleFormWrapper
        cloudAccounts={[]}
        pools={[]}
        onSubmit={vi.fn}
        onCancel={vi.fn}
        onPoolChange={vi.fn}
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
    </TestProvider>
  );
  root.unmount();
});
