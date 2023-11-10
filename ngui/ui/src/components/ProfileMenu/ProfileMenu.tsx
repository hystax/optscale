import { useCallback, useState } from "react";
import AccountCircleOutlinedIcon from "@mui/icons-material/AccountCircleOutlined";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import Avatar from "@mui/material/Avatar";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import MenuList from "@mui/material/MenuList";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import MenuItem from "components/MenuItem";
import Tooltip from "components/Tooltip";
import { useSignOut } from "hooks/useSignOut";
import { getInitialsFromName, isEllipsisActive } from "utils/strings";
import useStyles from "./ProfileMenu.styles";

const ProfileItemLabel = ({ dataTestId, variant, label }) => {
  const [isOverflow, setIsOverflow] = useState(false);

  const ref = useCallback((node) => {
    if (node !== null) {
      setIsOverflow(isEllipsisActive(node));
    }
  }, []);

  const getLabel = (
    <Typography style={{ display: "block" }} data-test-id={dataTestId} variant={variant} noWrap ref={ref}>
      {label}
    </Typography>
  );

  return isOverflow ? <Tooltip title={label}>{getLabel}</Tooltip> : getLabel;
};

const ProfileMenu = ({ name, email, isLoading }) => {
  const { classes } = useStyles();

  const getProfileIcon = (nameString) => getInitialsFromName(nameString) || <AccountCircleOutlinedIcon />;

  const signOut = useSignOut();

  const menuItems = [
    // {
    //   messageId: "settings",
    //   icon: SettingsOutlinedIcon,
    //   key: "settingsKey"
    // },
    {
      messageId: "signOut",
      icon: ExitToAppOutlinedIcon,
      onClick: () => {
        signOut();
      },
      dataTestId: "btn_signout",
      key: "signOutKey"
    }
  ];

  return (
    <Card className={classes.card}>
      <CardHeader
        avatar={
          isLoading ? (
            <Skeleton variant="circular" width={40} height={40} />
          ) : (
            <Avatar data-test-id="img_avatar" aria-label="recipe">
              {getProfileIcon(name)}
            </Avatar>
          )
        }
        title={
          isLoading ? (
            <>
              <Skeleton />
              <Skeleton height={16} />
            </>
          ) : (
            <>
              <ProfileItemLabel label={name} dataTestId="p_user_name" variant="subtitle1" />
              <ProfileItemLabel label={email} dataTestId="p_user_email" variant="caption" />
            </>
          )
        }
      />
      <CardContent className={classes.cardContent}>
        <MenuList>
          {menuItems.map((item) => (
            <MenuItem
              dataTestId={item.dataTestId}
              key={item.key}
              messageId={item.messageId}
              onClick={item.onClick}
              icon={item.icon}
            />
          ))}
        </MenuList>
      </CardContent>
    </Card>
  );
};

export default ProfileMenu;
