import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import Backdrop from "./Backdrop";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Backdrop>
        <CircularProgress />
      </Backdrop>
    </TestProvider>
  );
  root.unmount();
});
