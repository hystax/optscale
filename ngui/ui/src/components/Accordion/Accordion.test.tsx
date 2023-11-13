import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Accordion from "./Accordion";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Accordion>
        <div>Summary</div>
        <div>Details</div>
      </Accordion>
    </TestProvider>
  );
  root.unmount();
});
