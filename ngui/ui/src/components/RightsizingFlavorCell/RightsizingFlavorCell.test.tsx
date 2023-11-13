import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RightsizingFlavorCell from "./RightsizingFlavorCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RightsizingFlavorCell flavorName="name" flavorCpu={1} />
    </TestProvider>
  );
  root.unmount();
});
