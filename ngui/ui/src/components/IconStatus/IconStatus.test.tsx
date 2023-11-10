import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import IconStatus from "./IconStatus";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <IconStatus labelMessageId="optscale" color="error" />
    </TestProvider>
  );
  root.unmount();
});
