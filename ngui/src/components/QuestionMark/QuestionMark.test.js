import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import QuestionMark from "./QuestionMark";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <QuestionMark messageId="name" />
    </TestProvider>
  );
  root.unmount();
});
