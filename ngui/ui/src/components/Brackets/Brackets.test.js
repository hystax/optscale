import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Brackets from "./Brackets";

it("renders without crashing (empty props)", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Brackets />
    </TestProvider>
  );
  root.unmount();
});

it("renders without crashing (without children)", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Brackets type="round" bold />
    </TestProvider>
  );
  root.unmount();
});

it("renders without crashing (with children)", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Brackets type="round" bold>
        {"brackets content"}
      </Brackets>
    </TestProvider>
  );
  root.unmount();
});
