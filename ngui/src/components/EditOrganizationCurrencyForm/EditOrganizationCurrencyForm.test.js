import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EditOrganizationCurrencyForm from "./EditOrganizationCurrencyForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EditOrganizationCurrencyForm defaultCurrency="USD" onSubmit={jest.fn} onCancel={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
