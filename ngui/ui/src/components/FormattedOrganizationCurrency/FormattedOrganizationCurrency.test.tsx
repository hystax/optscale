import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import FormattedOrganizationCurrency from "./FormattedOrganizationCurrency";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <FormattedOrganizationCurrency currencyCode="EUR" />
    </TestProvider>
  );
  root.unmount();
});
