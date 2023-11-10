import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResetPassword from "./ResetPassword";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResetPassword onSubmit={() => console.log("submit")} isLoading={false} sendState="SUCCESS" />
    </TestProvider>
  );
  root.unmount();
});
