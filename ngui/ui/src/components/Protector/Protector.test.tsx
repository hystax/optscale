import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Protector from "./Protector";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Protector allowedActions={[]}>
        <div>test</div>
      </Protector>
    </TestProvider>
  );
  root.unmount();
});
