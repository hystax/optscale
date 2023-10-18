import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import GoalLabel from "./GoalLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <GoalLabel name="name" tendency="mode" goalValue={1} targetGoalValue={2} />
    </TestProvider>
  );
  root.unmount();
});
