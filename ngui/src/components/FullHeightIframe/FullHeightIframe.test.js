import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import FullHeightIframe from "./FullHeightIframe";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <FullHeightIframe
        source="https://hystax.com"
        iframeTitleMessageId="title"
        fallbackUrl="https://hystax.com"
        fallbackMessageId="unableToLoad"
        fallbackButtonMessageId="proceedToFinopsWebsite"
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
