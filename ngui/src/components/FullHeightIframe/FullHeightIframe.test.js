import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import FullHeightIframe from "./FullHeightIframe";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <FullHeightIframe
        source="https://hystax.com"
        iframeTitleMessageId="title"
        fallbackUrl="https://hystax.com"
        fallbackMessageId="unableToLoad"
        fallbackButtonMessageId="proceedToFinopsWebsite"
      />
    </TestProvider>
  );
  root.unmount();
});
