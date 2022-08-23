import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MapMarker from "./MapMarker";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MapMarker cloudType="test" region="test" value={1} startDateTimestamp="" endDateTimestamp="" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
