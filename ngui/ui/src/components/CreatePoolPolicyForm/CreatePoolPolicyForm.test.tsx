import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CreatePoolPolicyForm from "./CreatePoolPolicyForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CreatePoolPolicyForm pools={[]} />
    </TestProvider>
  );
  root.unmount();
});
