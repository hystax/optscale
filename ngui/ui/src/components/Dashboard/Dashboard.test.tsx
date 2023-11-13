import { createRoot } from "react-dom/client";
import { PRODUCT_TOUR } from "components/Tour";
import TestProvider from "tests/TestProvider";
import Dashboard from "./Dashboard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider
      state={{
        [PRODUCT_TOUR]: { isOpen: false, isFinished: false }
      }}
    >
      <Dashboard />
    </TestProvider>
  );
  root.unmount();
});
