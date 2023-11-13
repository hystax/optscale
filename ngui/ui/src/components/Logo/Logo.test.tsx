import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Logo from "./Logo";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Logo />
    </TestProvider>
  );
  root.unmount();
});
