import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ApplyResourcePerspective from "./ApplyResourcePerspective";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ApplyResourcePerspective perspectives={[]} onApply={vi.fn} onCancel={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});
