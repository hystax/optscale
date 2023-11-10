import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import LandingPage from "./LandingPage";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <LandingPage titleMessageId="hystax" featureMessageId="hystax" featureActionMessageId="hystax" featureUrl="https://" />
    </TestProvider>
  );
  root.unmount();
});
