import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ChartPaletteSettingsForm from "./ChartPaletteSettingsForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ChartPaletteSettingsForm palette="chart" options={[]} onUpdate={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
