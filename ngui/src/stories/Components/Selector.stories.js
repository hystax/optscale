import React, { useState } from "react";
import selectorsMock from "mocks/selectorsMock";
import Selector from "components/Selector";
import DomainOutlinedIcon from "@mui/icons-material/DomainOutlined";
import WorkOutlineOutlinedIcon from "@mui/icons-material/WorkOutlineOutlined";
import DynamicFeedOutlinedIcon from "@mui/icons-material/DynamicFeedOutlined";
import Icon from "components/Icon";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Selector`
};

export const basic = () => <Selector data={selectorsMock} labelId="organization" onChange={() => {}} />;

export const mobile = () => <Selector isMobile data={selectorsMock} labelId="organization" onChange={() => {}} />;

const DOMAIN = "domain";
const WORK = "word";
const FEED = "feed";
const WithItemIcons = () => {
  const [selected, setSelected] = useState("domain");

  const icons = {
    [DOMAIN]: DomainOutlinedIcon,
    [WORK]: WorkOutlineOutlinedIcon,
    [FEED]: DynamicFeedOutlinedIcon
  };

  const data = {
    selected,
    items: [
      {
        name: "DomainOutlinedIcon",
        value: DOMAIN
      },
      {
        name: "WorkOutlineOutlinedIcon",
        value: WORK
      },
      {
        name: "DynamicFeedOutlinedIcon",
        value: FEED
      }
    ]
  };
  return (
    <Selector
      data={data}
      dataKey="icons"
      labelId="name"
      menuItemIcon={{
        component: Icon, // Icon is a default component - it is used for demo purposes here
        getComponentProps: (itemInfo) => ({
          icon: icons[itemInfo.value]
        })
      }}
      onChange={(value) => setSelected(value)}
    />
  );
};

export const withItemIcons = () => <WithItemIcons />;
