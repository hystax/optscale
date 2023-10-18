import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TtlAnalysisForm from "./TtlAnalysisForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider
      state={{
        rangeDates: {}
      }}
    >
      <TtlAnalysisForm
        pools={[]}
        onSubmit={vi.fn}
        fieldNames={{
          poolFieldName: "poolFieldName",
          ttlModeFieldName: "ttlModeFieldName",
          customTtlFieldName: "customTtlFieldName",
          startDateFieldName: "startDateFieldName",
          endDateFieldName: "endDateFieldName"
        }}
        defaultValues={{}}
        isLoading={false}
        isPoolSelectorReadOnly={false}
      />
    </TestProvider>
  );
  root.unmount();
});
