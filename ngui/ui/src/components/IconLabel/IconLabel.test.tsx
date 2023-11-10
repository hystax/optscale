import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import IconLabel from "./IconLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <IconLabel icon={<CheckOutlinedIcon />} label="label" />
    </TestProvider>
  );
  root.unmount();
});
