import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EventsFilterForm from "./EventsFilterForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EventsFilterForm onSubmit={jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
