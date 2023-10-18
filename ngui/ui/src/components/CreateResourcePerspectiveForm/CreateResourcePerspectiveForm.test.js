import React from "react";
import { createRoot } from "react-dom/client";
import Filters from "components/Filters";
import TestProvider from "tests/TestProvider";
import CreateResourcePerspectiveForm from "./CreateResourcePerspectiveForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CreateResourcePerspectiveForm
        onSubmit={vi.fn}
        breakdownBy="tags"
        breakdownData={{}}
        filters={
          new Filters({
            filters: [],
            filterValues: {}
          })
        }
      />
    </TestProvider>
  );
  root.unmount();
});
