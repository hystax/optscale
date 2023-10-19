import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import InviteEmployees from "./InviteEmployees";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <InviteEmployees isLoadingProps={false} onSubmit={vi.fn} availablePools={[]} />
    </TestProvider>,
    div
  );
  root.unmount();
});
