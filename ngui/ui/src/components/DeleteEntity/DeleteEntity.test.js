import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DeleteEntity from "./DeleteEntity";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DeleteEntity
        message={{ messageId: "deleteResourcesQuestion", values: { count: 1 } }}
        deleteButtonProps={{
          onDelete: () => jest.fn
        }}
        onCancel={() => jest.fn}
      />
    </TestProvider>
  );
  root.unmount();
});
