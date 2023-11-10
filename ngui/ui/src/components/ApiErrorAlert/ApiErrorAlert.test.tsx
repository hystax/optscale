import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ApiErrorAlert from "./ApiErrorAlert";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider
      state={{
        api: { latestErrorLabel: "" }
      }}
    >
      <ApiErrorAlert />
    </TestProvider>
  );
  root.unmount();
});
