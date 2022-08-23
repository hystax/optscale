import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import UpcomingBooking from "./UpcomingBooking";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <UpcomingBooking employeeName="A" acquiredSince={0} releasedAt={1} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
