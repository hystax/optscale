import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ApiSuccessMessage from "./ApiSuccessMessage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ApiSuccessMessage successCode="FE0001" />
    </TestProvider>
  );
  root.unmount();
});
