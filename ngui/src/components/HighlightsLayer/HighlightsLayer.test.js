import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import HighlightsLayer from "./HighlightsLayer";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <HighlightsLayer
        chartOptions={{
          data: [
            {
              data: [{ x: 1 }]
            }
          ],
          xScale: jest.fn,
          innerHeight: 10,
          areaOpacity: 0.1
        }}
        shouldHighlight={jest.fn}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
