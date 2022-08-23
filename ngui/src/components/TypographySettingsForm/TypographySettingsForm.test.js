import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TypographySettingsForm from "./TypographySettingsForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TypographySettingsForm variant="body1" options={{}} onUpdate={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
