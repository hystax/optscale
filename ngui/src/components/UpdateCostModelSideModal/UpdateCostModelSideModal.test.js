import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import UpdateCostModelSideModal from "./UpdateCostModelSideModal";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <UpdateCostModelSideModal isOpen setIsOpen={jest.fn} cloudAccountId="cloudAccountId" costModel={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
