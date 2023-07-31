import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import GoalLabel from "./GoalLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <GoalLabel name="name" tendency="mode" goalValue={1} targetGoalValue={2} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
