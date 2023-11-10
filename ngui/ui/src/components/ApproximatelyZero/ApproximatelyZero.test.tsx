import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ApproximatelyZero from "./ApproximatelyZero";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ApproximatelyZero />
    </TestProvider>
  );
  root.unmount();
});
