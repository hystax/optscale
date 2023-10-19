import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ChartPaletteSettingsForm from "./ChartPaletteSettingsForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ChartPaletteSettingsForm palette="chart" options={[]} onUpdate={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});
