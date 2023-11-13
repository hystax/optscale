import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";
import Box from "@mui/material/Box";
import awsLogo from "assets/clouds/aws.svg";
import ActionBarHeader from "components/ActionBarHeader";
import Image from "components/Image";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ActionBarHeader`
};

export const basic = () => (
  <ActionBarHeader text="Text">
    <Box>Children</Box>
  </ActionBarHeader>
);
export const loading = () => (
  <ActionBarHeader isLoading text="Text">
    <Box>Children</Box>
  </ActionBarHeader>
);
export const withIcon = () => (
  <ActionBarHeader text="With test icon">
    <PersonOutlineOutlinedIcon />
  </ActionBarHeader>
);
export const withImage = () => (
  <ActionBarHeader text="With test image">
    <Image src={awsLogo} alt="altText" />
  </ActionBarHeader>
);
