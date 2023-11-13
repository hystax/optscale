import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RegionExpensesMap from "./RegionExpensesMap";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RegionExpensesMap markers={[]} defaultCenter={{ lat: 0, lng: 0 }} defaultZoom={1} />
    </TestProvider>
  );
  root.unmount();
});
