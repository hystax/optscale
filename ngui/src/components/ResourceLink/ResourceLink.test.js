import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { RESOURCE_PAGE_TABS } from "utils/constants";
import ResourceLink from "./ResourceLink";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceLink resourceId="id" tabName={RESOURCE_PAGE_TABS.EXPENSES}>
        resourceName
      </ResourceLink>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
