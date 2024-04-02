import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlTaskDetails from "./MlTaskDetails";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlTaskDetails task={{}} isLoading />
    </TestProvider>,
    div
  );
  root.unmount();
});
