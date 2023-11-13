import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { AWS_CNR } from "utils/constants";
import MapMarker from "./MapMarker";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MapMarker markerData={{ type: AWS_CNR }} startDateTimestamp="" endDateTimestamp="" />
    </TestProvider>
  );
  root.unmount();
});
