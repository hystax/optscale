import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Backdrop from "./Backdrop";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Backdrop>
        <CircularProgress />
      </Backdrop>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
