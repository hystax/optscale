import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ConnectForm from "./ConnectForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ConnectForm>{() => null}</ConnectForm>
    </TestProvider>
  );
  root.unmount();
});
