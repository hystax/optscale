import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ContentBackdropLoader from "./ContentBackdropLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ContentBackdropLoader />
    </TestProvider>
  );
  root.unmount();
});
