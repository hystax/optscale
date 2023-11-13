import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TabsLoader from "./TabsLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TabsLoader tabsCount={1} />
    </TestProvider>
  );
  root.unmount();
});
