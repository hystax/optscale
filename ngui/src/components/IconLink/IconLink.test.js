import React from "react";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import IconLink from "./IconLink";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <IconLink icon={{ logo: <CheckOutlinedIcon />, altMessageId: "test" }} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
