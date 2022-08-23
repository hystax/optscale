import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Tooltip from ".";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Tooltip
        backProps={{}}
        primaryProps={{}}
        skipProps={{}}
        tooltipProps={{}}
        continuous
        index={0}
        isLastStep={false}
        size={3}
        step={{}}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
