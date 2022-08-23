import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import SnackbarAlert from "./SnackbarAlert";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider
      state={{
        api: { latestErrorLabel: "" }
      }}
    >
      <SnackbarAlert text="test" openState={false} handleClose={(e) => console.log(e)} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
