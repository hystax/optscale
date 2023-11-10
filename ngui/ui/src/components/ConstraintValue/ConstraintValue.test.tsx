import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ConstraintValue from "./ConstraintValue";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ConstraintValue hitValue={120} constraintLimit={100} type="test" />
    </TestProvider>
  );
  root.unmount();
});
