import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import MlModelRecommendations from "./MlModelRecommendations";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MlModelRecommendations recommendations={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
