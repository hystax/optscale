import { useState } from "react";
import DomainOutlinedIcon from "@mui/icons-material/DomainOutlined";
import DynamicFeedOutlinedIcon from "@mui/icons-material/DynamicFeedOutlined";
import WorkOutlineOutlinedIcon from "@mui/icons-material/WorkOutlineOutlined";
import Icon from "components/Icon";
import Selector from "components/Selector";

export default {
  component: Selector
};

const data = {
  selected: "",
  items: [
    {
      id: 1,
      name: "CommunityMSP.org",
      isRoot: true
    },
    {
      id: 2,
      name: "Acme Inc",
      value: "acme"
    },
    {
      id: 3,
      name: "FutureOps.com",
      value: "futureops"
    },
    {
      id: 4,
      name: "AnyWhereGo LLC",
      value: "anywherego"
    }
  ]
};

export const basic = () => <Selector data={data} labelId="organization" onChange={() => {}} />;

export const mobile = () => <Selector isMobile data={data} labelId="organization" onChange={() => {}} />;

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
