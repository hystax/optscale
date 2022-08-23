import React from "react";
import MenuIcon from "@mui/icons-material/Menu";
import ReactDOM from "react-dom";
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
  ReactDOM.render(
    <TestProvider>
      <ActionBar data={items} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
