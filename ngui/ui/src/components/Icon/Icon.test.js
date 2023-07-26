import React from "react";
import ErrorIcon from "@mui/icons-material/Error";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Icon from "./Icon";

it("renders without crashing without children", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Icon icon={ErrorIcon} />
    </TestProvider>
  );
  root.unmount();
});
