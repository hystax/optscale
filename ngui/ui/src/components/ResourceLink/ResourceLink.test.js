import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { RESOURCE_PAGE_TABS } from "utils/constants";
import ResourceLink from "./ResourceLink";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceLink resourceId="id" tabName={RESOURCE_PAGE_TABS.EXPENSES}>
        resourceName
      </ResourceLink>
    </TestProvider>
  );
  root.unmount();
});
