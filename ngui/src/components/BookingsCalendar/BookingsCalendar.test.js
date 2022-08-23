import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import BookingsCalendar from "./BookingsCalendar";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <BookingsCalendar environments={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
