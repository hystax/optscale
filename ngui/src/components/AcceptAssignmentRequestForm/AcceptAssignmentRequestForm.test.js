import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import AcceptAssignmentRequestForm from "./AcceptAssignmentRequestForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <AcceptAssignmentRequestForm resourceName="" assignmentRequestId="" closeSideModal={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
