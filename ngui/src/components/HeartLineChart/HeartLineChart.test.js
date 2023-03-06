import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import HeartLineChart from "./HeartLineChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <HeartLineChart values={[0]} redZoneValue={0} average={0} width={100} height={100} />
    </TestProvider>
  );
  root.unmount();
});
