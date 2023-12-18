import BusinessIcon from "@mui/icons-material/Business";
import CloudIcon from "@mui/icons-material/Cloud";
import PeopleIcon from "@mui/icons-material/People";
import ButtonSwitch from "components/ButtonSwitch";

export default {
  component: ButtonSwitch
};

const buttons = [
  { messageId: "cloud", link: "/", icon: <CloudIcon /> },
  { messageId: "pool", link: "/", icon: <BusinessIcon /> },
  { messageId: "owner", link: "/", icon: <PeopleIcon /> }
];

export const basic = () => <ButtonSwitch buttons={buttons} />;
