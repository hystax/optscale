import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import AcceptInvitation from "./AcceptInvitation";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <AcceptInvitation invitation={{}} onAccept={() => {}} onDecline={() => {}} isUpdateLoading />
    </TestProvider>
  );
  root.unmount();
});
