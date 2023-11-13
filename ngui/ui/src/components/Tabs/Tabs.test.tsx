import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Tabs from "./Tabs";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Tabs>[]</Tabs>
    </TestProvider>
  );
  root.unmount();
});
