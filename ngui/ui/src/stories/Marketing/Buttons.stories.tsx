import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import CloudIcon from "@mui/icons-material/Cloud";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import MenuBookOutlinedIcon from "@mui/icons-material/MenuBookOutlined";
import PersonAddOutlinedIcon from "@mui/icons-material/PersonAddOutlined";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Button from "components/Button";
import ButtonGroup from "components/ButtonGroup";
import IconButton from "components/IconButton";
import WrapperCard from "components/WrapperCard";

export default {
  title: "Marketing/Buttons"
};

const renderButtons = (buttons) => (
  <Box display="flex">
    {buttons.map((props) => (
      <Box key={props.key} mr={1}>
        <Button {...props} />
      </Box>
    ))}
  </Box>
);

const renderIconButtons = (buttons) => (
  <Box display="flex">
    {buttons.map((props) => (
      <Box key={props.key} mr={1}>
        <IconButton {...props} />
      </Box>
    ))}
  </Box>
);

const Contained = () => (
  <WrapperCard title="Contained">
    <Typography>All colors:</Typography>
    {renderButtons([
      {
        text: "primary",
        key: "primaryContained",
        color: "primary",
        variant: "contained"
      },
      {
        text: "secondary",
        key: "secondaryContained",
        color: "secondary",
        variant: "contained"
      },
      {
        text: "success",
        key: "successContained",
        color: "success",
        variant: "contained"
      },
      {
        text: "info",
        key: "infoContained",
        color: "info",
        variant: "contained"
      },
      {
        text: "error",
        key: "errorContained",
        color: "error",
        variant: "contained"
      }
    ])}
    <Typography>All colors with icons:</Typography>
    {renderButtons([
      {
        text: "primary",
        key: "primaryContainedWithIcon",
        color: "primary",
        variant: "contained",
        startIcon: <AddOutlinedIcon />
      },
      {
        text: "secondary",
        key: "secondaryContainedWithIcon",
        color: "secondary",
        variant: "contained",
        startIcon: <PersonAddOutlinedIcon />
      },
      {
        text: "success",
        key: "successContainedWithIcon",
        color: "success",
        variant: "contained",
        startIcon: <CloudIcon />
      },
      {
        text: "info",
        key: "infoContainedWithIcon",
        color: "info",
        variant: "contained",
        startIcon: <EditOutlinedIcon />
      },
      {
        key: "errorContainedWithIcon",
        text: "error",
        color: "error",
        variant: "contained",
        startIcon: <DeleteOutlinedIcon />
      }
    ])}
    <Typography>Sizes:</Typography>
    {renderButtons([
      {
        text: "small",
        key: "primaryContainedSmall",
        color: "primary",
        variant: "contained",
        size: "small"
      },
      {
        text: "medium",
        key: "primaryContainedMedium",
        color: "primary",
        variant: "contained",
        size: "medium"
      },
      {
        text: "large",
        key: "primaryContainedLarge",
        color: "primary",
        variant: "contained",
        size: "large"
      }
    ])}
  </WrapperCard>
);

const Outlined = () => (
  <WrapperCard title="Outlined">
    <Typography>All colors:</Typography>
    {renderButtons([
      {
        text: "primary",
        key: "primaryOutlined",
        color: "primary",
        variant: "outlined"
      },
      {
        text: "secondary",
        key: "secondaryOutlined",
        color: "secondary",
        variant: "outlined"
      },
      {
        text: "success",
        key: "successOutlined",
        color: "success",
        variant: "outlined"
      },
      {
        text: "info",
        key: "infoOutlined",
        color: "info",
        variant: "outlined"
      },
      {
        text: "error",
        key: "errorOutlined",
        color: "error",
        variant: "outlined"
      }
    ])}
    <Typography>All colors with icons:</Typography>
    {renderButtons([
      {
        text: "primary",
        key: "primaryOutlinedWithIcon",
        color: "primary",
        variant: "outlined",
        startIcon: <AddOutlinedIcon />
      },
      {
        text: "secondary",
        key: "secondaryOutlinedWithIcon",
        color: "secondary",
        variant: "outlined",
        startIcon: <PersonAddOutlinedIcon />
      },
      {
        text: "success",
        key: "successOutlinedWithIcon",
        color: "success",
        variant: "outlined",
        startIcon: <CloudIcon />
      },
      {
        text: "info",
        key: "infoOutlinedWithIcon",
        color: "info",
        variant: "outlined",
        startIcon: <EditOutlinedIcon />
      },
      {
        text: "error",
        key: "errorOutlinedWithIcon",
        color: "error",
        variant: "outlined",
        startIcon: <DeleteOutlinedIcon />
      }
    ])}
    <Typography>Sizes:</Typography>
    {renderButtons([
      {
        text: "small",
        key: "primaryOutlinedSmall",
        color: "primary",
        variant: "outlined",
        size: "small"
      },
      {
        text: "medium",
        key: "primaryOutlinedMedium",
        color: "primary",
        variant: "outlined",
        size: "medium"
      },
      {
        text: "large",
        key: "primaryOutlinedLarge",
        color: "primary",
        variant: "outlined",
        size: "large"
      }
    ])}
  </WrapperCard>
);

const Text = () => (
  <WrapperCard title="Text">
    <Typography>All colors:</Typography>
    {renderButtons([
      {
        text: "default",
        key: "defaultText",
        variant: "text"
      },
      {
        text: "primary",
        key: "primaryText",
        color: "primary",
        variant: "text"
      }
    ])}
    <Typography>All colors with icons:</Typography>
    {renderButtons([
      {
        text: "default",
        key: "defaultTextWithIcon",
        variant: "text",
        startIcon: <AddOutlinedIcon />
      },
      {
        text: "primary",
        key: "primaryTextWithIcon",
        color: "primary",
        variant: "text",
        startIcon: <PersonAddOutlinedIcon />
      }
    ])}
    <Typography>Sizes:</Typography>
    {renderButtons([
      {
        text: "small",
        key: "primaryTextSmall",
        variant: "text",
        color: "primary",
        size: "small"
      },
      {
        text: "medium",
        key: "primaryTextMedium",
        variant: "text",
        color: "primary",
        size: "medium"
      },
      {
        text: "large",
        variant: "text",
        key: "primaryTextLarge",
        color: "primary",
        size: "large"
      }
    ])}
  </WrapperCard>
);

const GroupedButtons = () => (
  <WrapperCard title="ButtonGroup">
    <Typography>Only one variant is supported:</Typography>
    <ButtonGroup
      activeButtonIndex={0}
      buttons={[
        { id: "owner", messageId: "owner" },
        { id: "service", messageId: "service" }
      ]}
    />
  </WrapperCard>
);

const IconButtons = () => (
  <WrapperCard title="IconButton">
    <Typography>Colors (there are tooltips with color information and sizes):</Typography>
    {renderIconButtons([
      {
        tooltip: { show: true, value: "inherit" },
        key: "inheritIconButton",
        color: "inherit",
        icon: <MenuBookOutlinedIcon />
      },
      {
        tooltip: { show: true, value: "primary" },
        key: "primaryIconButton",
        color: "primary",
        icon: <CloudDownloadOutlinedIcon />
      },
      {
        tooltip: { show: true, value: "success" },
        key: "successIconButton",
        color: "success",
        icon: <AccountCircleIcon />
      },
      {
        tooltip: { show: true, value: "error" },
        key: "errorIconButton",
        color: "error",
        icon: <DeleteOutlinedIcon />
      },
      {
        tooltip: { show: true, value: "info" },
        key: "infoIconButton",
        color: "info",
        icon: <EditOutlinedIcon />
      }
    ])}
    <Typography>Sizes:</Typography>
    {renderIconButtons([
      {
        tooltip: { show: true, value: "small" },
        key: "primaryIconButtonSmall",
        size: "small",
        color: "primary",
        icon: <MenuBookOutlinedIcon />
      },
      {
        tooltip: { show: true, value: "medium" },
        key: "primaryIconButtonMedium",
        size: "medium",
        color: "primary",
        icon: <MenuBookOutlinedIcon />
      }
    ])}
  </WrapperCard>
);

export const basic = () => (
  <>
    <Box mb={2}>
      <WrapperCard>
        <Typography>We use these guides:</Typography>
        <ul>
          <li>
            <Typography>
              <a href="https://material.io/components/buttons" target="_blank" rel="noreferrer">
                Material Design
              </a>
            </Typography>
          </li>
          <li>
            <Typography>
              <a href="https://material-ui.com/components/buttons/" target="_blank" rel="noreferrer">
                Material ui
              </a>
            </Typography>
          </li>
          <li>
            <Typography>
              <a href="https://material-ui.com/components/material-icons/" target="_blank" rel="noreferrer">
                Icons
              </a>
            </Typography>
          </li>
        </ul>
      </WrapperCard>
    </Box>
    <Box mb={2}>
      <Contained />
    </Box>
    <Box mb={2}>
      <Outlined />
    </Box>
    <Box mb={2}>
      <Text />
    </Box>
    <Box mb={2}>
      <GroupedButtons />
    </Box>
    <Box mb={2}>
      <IconButtons />
    </Box>
  </>
);
