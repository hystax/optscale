import React from "react";
import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ActionBarHeader from "./ActionBarHeader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ActionBarHeader text="test">
        <PersonOutlineOutlinedIcon />
      </ActionBarHeader>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
