import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ActionBarHeader from "./ActionBarHeader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ActionBarHeader text="test">
        <PersonOutlineOutlinedIcon />
      </ActionBarHeader>
    </TestProvider>
  );
  root.unmount();
});
