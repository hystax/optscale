import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlRunStatusHeaderCell from "./MlRunStatusHeaderCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlRunStatusHeaderCell />
    </TestProvider>
  );
  root.unmount();
});
