import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import HighlightsLayer from "./HighlightsLayer";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <HighlightsLayer
        chartOptions={{
          data: [
            {
              data: [{ x: 1 }]
            }
          ],
          xScale: vi.fn,
          innerHeight: 10,
          areaOpacity: 0.1
        }}
        shouldHighlight={vi.fn}
      />
    </TestProvider>
  );
  root.unmount();
});
