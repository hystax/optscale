import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import IconLink from "./IconLink";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <IconLink icon={{ logo: <CheckOutlinedIcon />, altMessageId: "test" }} />
    </TestProvider>
  );
  root.unmount();
});
