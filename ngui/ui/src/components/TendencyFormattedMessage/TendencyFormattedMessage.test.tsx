import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TendencyFormattedMessage from "./TendencyFormattedMessage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TendencyFormattedMessage tendency="more" />
    </TestProvider>
  );
  root.unmount();
});
