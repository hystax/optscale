import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RegistrationForm from "./RegistrationForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RegistrationForm onSubmit={() => console.log("submit")} isLoading={false} sendState="SUCCESS" />
    </TestProvider>
  );
  root.unmount();
});
