import { createRoot } from "react-dom/client";
import { FormattedMessage } from "react-intl";
import TestProvider from "tests/TestProvider";
import ErrorBoundary from "./ErrorBoundary";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ErrorBoundary>
        <FormattedMessage id="hystax" />
      </ErrorBoundary>
    </TestProvider>
  );
  root.unmount();
});

it("renders without crashing with buggy component", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ErrorBoundary>
        <FormattedMessage />
      </ErrorBoundary>
    </TestProvider>
  );
  root.unmount();
});
