import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlTaskCreate from "./MlTaskCreate";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlTaskCreate />
    </TestProvider>
  );
  root.unmount();
});
