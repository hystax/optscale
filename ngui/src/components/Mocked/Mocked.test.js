import React from "react";
import ReactDOM from "react-dom";
import { PRODUCT_TOUR } from "components/ProductTour";
import TestProvider from "tests/TestProvider";
import Mocked from "./Mocked";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        [PRODUCT_TOUR]: { isOpen: false, isFinished: false }
      }}
    >
      <Mocked mock={<div>Mock</div>}>
        <div>Component</div>
      </Mocked>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
