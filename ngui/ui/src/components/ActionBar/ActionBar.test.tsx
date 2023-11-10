import MenuIcon from "@mui/icons-material/Menu";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ActionBar from "./ActionBar";

const items = {
  show: true,
  key: "key",
  title: "add",
  items: [
    {
      key: "item-key",
      icon: <MenuIcon fontSize="small" />,
      messageId: "edit",
      link: "#",
      type: "button",
      title: "title"
    }
  ]
};

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ActionBar data={items} />
    </TestProvider>
  );
  root.unmount();
});
