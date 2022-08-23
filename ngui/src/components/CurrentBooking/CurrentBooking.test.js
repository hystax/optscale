import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CurrentBooking from "./CurrentBooking";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CurrentBooking employeeName="A" acquiredSince={1} releasedAt={2} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
