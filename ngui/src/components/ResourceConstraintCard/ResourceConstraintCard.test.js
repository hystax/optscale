import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ResourceConstraintCard from "./ResourceConstraintCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ResourceConstraintCard
        updateConstraint={() => console.log("update")}
        createConstraint={() => console.log("create")}
        deleteConstraint={() => console.log("deleteConstraint")}
        constraint={{}}
        constraintType="ttl"
        poolPolicy={{}}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
