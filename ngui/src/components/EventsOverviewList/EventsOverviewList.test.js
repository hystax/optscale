import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EventsOverviewList from "./EventsOverviewList";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EventsOverviewList events={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
