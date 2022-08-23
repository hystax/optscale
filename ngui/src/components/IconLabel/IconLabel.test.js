import React from "react";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import IconLabel from "./IconLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <IconLabel icon={<CheckOutlinedIcon />} label="label" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
