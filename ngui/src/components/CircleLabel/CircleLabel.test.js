import React from "react";
import ReactDOM from "react-dom";
import CircleLabel from "./CircleLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(<CircleLabel />, div);
  ReactDOM.unmountComponentAtNode(div);
});
