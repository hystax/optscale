import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ApiErrorMessage from "./ApiErrorMessage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ApiErrorMessage errorCode="OEXXX" reason="reason" url="https://" params={[]} />
    </TestProvider>
  );
  root.unmount();
});
