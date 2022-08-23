import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Month from "./Month";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Month
        value={new Date()}
        dateRange={{ startDate: new Date(), endDate: new Date() }}
        minDate={new Date()}
        maxDate={new Date()}
        helpers={{ inHoverRange: () => {} }}
        userBounds={{ minDate: 0, maxDate: 0 }}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
