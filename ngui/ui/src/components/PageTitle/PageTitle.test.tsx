import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PageTitle from "./PageTitle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PageTitle />
    </TestProvider>
  );
  root.unmount();
});
