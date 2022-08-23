import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import GoogleCalendar from "./GoogleCalendar";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <GoogleCalendar calendarSynchronization={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
