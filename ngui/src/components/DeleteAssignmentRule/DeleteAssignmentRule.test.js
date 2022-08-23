import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { UNKNOWN } from "utils/constants";
import DeleteAssignmentRule from "./DeleteAssignmentRule";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DeleteAssignmentRule isLoading={false} onSubmit={jest.fn} sendState={UNKNOWN} setModalOpen={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
