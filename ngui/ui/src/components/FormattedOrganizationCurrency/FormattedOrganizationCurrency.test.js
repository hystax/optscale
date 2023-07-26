import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import FormattedOrganizationCurrency from "./FormattedOrganizationCurrency";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <FormattedOrganizationCurrency currencyCode="EUR" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
