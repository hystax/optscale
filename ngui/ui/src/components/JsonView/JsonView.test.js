import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import JsonView from "./JsonView";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <JsonView value={{}} onChange={vi.fn} />
    </TestProvider>,
    div
  );
  root.unmount();
});
