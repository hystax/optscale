import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import EditPoolPolicyLimitForm from "./EditPoolPolicyLimitForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <EditPoolPolicyLimitForm />
    </TestProvider>
  );
  root.unmount();
});
