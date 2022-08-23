import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TtlAnalysisForm from "./TtlAnalysisForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        rangeDates: {}
      }}
    >
      <TtlAnalysisForm
        pools={[]}
        onSubmit={jest.fn}
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
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
