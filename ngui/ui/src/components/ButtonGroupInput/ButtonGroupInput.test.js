import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ButtonGroupInput from "./ButtonGroupInput";

it("renders with action", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ButtonGroupInput labelText="" helperText="" buttons={[]} activeButtonIndex={0} />
    </TestProvider>
  );
  root.unmount();
});
