import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MailTo from "./MailTo";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MailTo email="test@test.com" text="test@test.com" />
    </TestProvider>
  );
  root.unmount();
});
