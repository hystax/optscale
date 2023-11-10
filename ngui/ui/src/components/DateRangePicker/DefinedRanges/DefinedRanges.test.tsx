import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DefinedRanges from "./DefinedRanges";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DefinedRanges ranges={[]} />
    </TestProvider>
  );
  root.unmount();
});
