import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ButtonSwitch from "./ButtonSwitch";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ButtonSwitch buttons={[]} />
    </TestProvider>
  );
  root.unmount();
});
