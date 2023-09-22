import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import S3DuplicatesChecksTable from "./S3DuplicateFinderCheck";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <S3DuplicatesChecksTable />
    </TestProvider>
  );
  root.unmount();
});
