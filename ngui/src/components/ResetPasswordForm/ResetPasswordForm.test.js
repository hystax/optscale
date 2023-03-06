import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResetPasswordForm from "./ResetPasswordForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResetPasswordForm onSubmit={() => console.log("submit")} isLoading={false} sendState="SUCCESS" />
    </TestProvider>
  );
  root.unmount();
});
