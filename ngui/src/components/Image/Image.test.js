import React from "react";
import ReactDOM from "react-dom";
import awsLogo from "assets/clouds/aws.svg";
import TestProvider from "tests/TestProvider";
import Image from "./Image";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Image src={awsLogo} alt="altText" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
