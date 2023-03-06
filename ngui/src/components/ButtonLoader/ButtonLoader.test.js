import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ButtonLoader from "./ButtonLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  const testAction = () => {
    console.log("test");
  };
  root.render(
    <TestProvider>
      <ButtonLoader messageId="checkConnection" onClick={testAction} isLoading={false} />
    </TestProvider>
  );
  root.unmount();
});
