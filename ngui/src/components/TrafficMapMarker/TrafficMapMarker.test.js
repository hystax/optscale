import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TrafficMapMarker from "./TrafficMapMarker";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TrafficMapMarker type="test" onClick={() => jest.fn} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
