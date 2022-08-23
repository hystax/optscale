import React from "react";
import ReactDOM from "react-dom";
import { PRODUCT_TOUR } from "components/ProductTour";
import TestProvider from "tests/TestProvider";
import MainMenu from "./MainMenu";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        mainMenuItems: [],
        auth: { GET_TOKEN: { userId: "123" } },
        [PRODUCT_TOUR]: { isOpen: false }
      }}
    >
      <MainMenu auth={{ GET_TOKEN: 1 }} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
