import React from "react";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import IconLabelGrid from "./IconLabelGrid";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <IconLabelGrid startIcon={<EditOutlinedIcon />} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
