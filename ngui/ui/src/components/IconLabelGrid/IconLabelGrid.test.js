import React from "react";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import IconLabelGrid from "./IconLabelGrid";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <IconLabelGrid startIcon={<EditOutlinedIcon />} />
    </TestProvider>
  );
  root.unmount();
});
