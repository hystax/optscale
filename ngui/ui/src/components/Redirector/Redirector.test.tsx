import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Redirector from "./Redirector";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Redirector condition={1 > 0} to={"/"}>
        <div>test</div>
      </Redirector>
    </TestProvider>
  );
  root.unmount();
});
