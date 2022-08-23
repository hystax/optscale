import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PaletteSettingsForm from "./PaletteSettingsForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PaletteSettingsForm color="primary" options={{}} onUpdate={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
