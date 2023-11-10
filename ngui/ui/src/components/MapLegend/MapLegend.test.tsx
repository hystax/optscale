import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MapLegend from "./MapLegend";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MapLegend markers={[]} />
    </TestProvider>
  );
  root.unmount();
});
