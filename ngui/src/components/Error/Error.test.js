import React from "react";
import { createRoot } from "react-dom/client";
import Error from "components/Error";
import TestProvider from "tests/TestProvider";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Error messageId="notFound" />
    </TestProvider>
  );
  root.unmount();
});
