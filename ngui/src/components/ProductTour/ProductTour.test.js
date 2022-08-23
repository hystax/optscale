import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ProductTour, { PRODUCT_TOUR } from ".";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        [PRODUCT_TOUR]: { isOpen: false, isFinished: false }
      }}
    >
      <ProductTour />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
