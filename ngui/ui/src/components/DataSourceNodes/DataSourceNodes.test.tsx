import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DataSourceNodes from "./DataSourceNodes";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DataSourceNodes cloudAccountId="cloudAccountId" costModel={{}} nodes={[]} />
    </TestProvider>
  );
  root.unmount();
});
