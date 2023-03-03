import React from "react";
import { createRoot } from "react-dom/client";
import Button from "components/Button";
import TestProvider from "tests/TestProvider";
import IconError from "./IconError";

it("renders without crashing without children", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <IconError messageId="hystax" />
    </TestProvider>
  );
  root.unmount();
});

it("renders without crashing with children", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <IconError messageId="hystax" />
      <Button variant="contained" color="primary" messageId="hystax" />
    </TestProvider>
  );
  root.unmount();
});
