import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ButtonGroup from "./ButtonGroup";

it("renders with action", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ButtonGroup
        activeButtonIndex={0}
        buttons={[
          {
            id: "add",
            messageId: "add",
            onClick: (e) => console.log(e)
          }
        ]}
      />
    </TestProvider>
  );
  root.unmount();
});
