import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlRunsetConfigurationForm from "./MlRunsetConfigurationForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlRunsetConfigurationForm runsetTemplate={{}} />
    </TestProvider>
  );
  root.unmount();
});
