import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SelectorLoader from "./SelectorLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SelectorLoader labelId="hystax" isRequired />
    </TestProvider>
  );
  root.unmount();
});
