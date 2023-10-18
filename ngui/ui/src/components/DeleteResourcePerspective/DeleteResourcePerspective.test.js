import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DeleteResourcePerspective from "./DeleteResourcePerspective";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DeleteResourcePerspective perspectiveName="name" onDelete={vi.fn} onCancel={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});
