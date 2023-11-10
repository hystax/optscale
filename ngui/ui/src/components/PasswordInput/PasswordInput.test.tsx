import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PasswordInput from "./PasswordInput";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PasswordInput />
    </TestProvider>
  );
  root.unmount();
});
