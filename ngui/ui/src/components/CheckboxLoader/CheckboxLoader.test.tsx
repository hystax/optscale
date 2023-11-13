import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CheckboxLoader from "./CheckboxLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CheckboxLoader />
    </TestProvider>
  );
  root.unmount();
});
