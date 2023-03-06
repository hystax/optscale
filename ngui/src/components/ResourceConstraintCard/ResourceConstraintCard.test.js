import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceConstraintCard from "./ResourceConstraintCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceConstraintCard
        updateConstraint={() => console.log("update")}
        createConstraint={() => console.log("create")}
        deleteConstraint={() => console.log("deleteConstraint")}
        constraint={{}}
        constraintType="ttl"
        poolPolicy={{}}
      />
    </TestProvider>
  );
  root.unmount();
});
