import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import IconButton from "./IconButton";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <IconButton icon={<EditOutlinedIcon />} />
    </TestProvider>
  );
  root.unmount();
});
