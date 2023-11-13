import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SlicedText from "./SlicedText";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SlicedText limit={1} text="test" />
    </TestProvider>
  );
  root.unmount();
});
