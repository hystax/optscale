import React from "react";
import ReactDOM from "react-dom";
import { FormattedMessage } from "react-intl";
import TestProvider from "tests/TestProvider";
import ErrorBoundary from "./ErrorBoundary";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ErrorBoundary>
        <FormattedMessage id="hystax" />
      </ErrorBoundary>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

it("renders without crashing with buggy component", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ErrorBoundary>
        <FormattedMessage />
      </ErrorBoundary>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
