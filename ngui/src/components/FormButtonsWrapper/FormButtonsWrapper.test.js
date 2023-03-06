import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import FormButtonsWrapper from "./FormButtonsWrapper";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <FormButtonsWrapper>
        <div>child</div>
      </FormButtonsWrapper>
    </TestProvider>
  );
  root.unmount();
});
