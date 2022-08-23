import React, { useEffect, useState } from "react";
import AccountCircleOutlinedIcon from "@mui/icons-material/AccountCircleOutlined";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import Avatar from "@mui/material/Avatar";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import MenuList from "@mui/material/MenuList";
import Skeleton from "@mui/material/Skeleton";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";
import MenuItem from "components/MenuItem";
import Tooltip from "components/Tooltip";
import { SIGNOUT } from "urls";
import { getInitialsFromName, isEllipsisActive } from "utils/strings";
import useStyles from "./ProfileMenu.styles";

const ProfileMenu = ({ name, email, isLoading }) => {
  const { classes } = useStyles();

  const navigate = useNavigate();

  const nameRef = React.createRef();
  const emailRef = React.createRef();

  const [isNameOverflow, setNameEllipsis] = useState(false);
  const [isEmailOverflow, setEmailEllipsis] = useState(false);

  useEffect(() => {
    setNameEllipsis(isEllipsisActive(nameRef));
    setEmailEllipsis(isEllipsisActive(emailRef));
  }, [nameRef, emailRef]);

  const getProfileIcon = (nameString) => getInitialsFromName(nameString) || <AccountCircleOutlinedIcon />;

  const renderString = ({ string, ref, variant, dataTestId }) => (
    <Typography data-test-id={dataTestId} variant={variant} noWrap ref={ref}>
      {string}
    </Typography>
  );

  const buildString = ({ condition, string, ref, variant, dataTestId }) =>
    condition ? (
      <Tooltip title={string}>{renderString({ string, ref, variant, dataTestId })}</Tooltip>
    ) : (
      renderString({ string, ref, variant, dataTestId })
    );

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
        navigate(SIGNOUT);
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
            <Skeleton />
          ) : (
            buildString({
              condition: isNameOverflow,
              string: name,
              ref: nameRef,
              variant: "subtitle1",
              dataTestId: "p_user_name"
            })
          )
        }
        subheader={
          isLoading ? (
            <Skeleton height={16} />
          ) : (
            buildString({
              condition: isEmailOverflow,
              string: email,
              ref: emailRef,
              variant: "caption",
              dataTestId: "p_user_email"
            })
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

ProfileMenu.propTypes = {
  name: PropTypes.string.isRequired,
  email: PropTypes.string.isRequired,
  isLoading: PropTypes.bool.isRequired
};

export default ProfileMenu;
