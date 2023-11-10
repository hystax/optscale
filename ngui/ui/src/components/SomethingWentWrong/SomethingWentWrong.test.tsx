import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SomethingWentWrong from "./SomethingWentWrong";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SomethingWentWrong />
    </TestProvider>
  );
  root.unmount();
});
