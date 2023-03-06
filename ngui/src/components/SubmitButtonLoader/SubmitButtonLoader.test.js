import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SubmitButtonLoader from "./SubmitButtonLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SubmitButtonLoader isLoading messageId="name" />
    </TestProvider>
  );
  root.unmount();
});
