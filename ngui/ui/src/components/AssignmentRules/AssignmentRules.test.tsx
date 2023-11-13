import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import AssignmentRules from "./AssignmentRules";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <AssignmentRules rules={{}} />
    </TestProvider>
  );
  root.unmount();
});
