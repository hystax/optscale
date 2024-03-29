import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlEditTask from "./MlEditTask";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlEditTask task={{}} />
    </TestProvider>
  );
  root.unmount();
});
