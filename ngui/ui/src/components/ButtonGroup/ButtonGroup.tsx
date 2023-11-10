import MuiButton from "@mui/material/Button";
import MuiButtonGroup from "@mui/material/ButtonGroup";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link } from "react-router-dom";
import Tooltip from "components/Tooltip";
import useStyles from "./ButtonGroup.styles";

const ButtonGroup = ({ buttons, activeButtonIndex, activeButtonId, fullWidth }) => {
  const { classes, cx } = useStyles();

  const findButtonIndexById = (idToFind) => buttons.find(({ id }) => id === idToFind);

  const activeButton = Number.isInteger(activeButtonIndex) ? buttons[activeButtonIndex] : findButtonIndexById(activeButtonId);

  const renderButtons = () =>
    buttons.map((button) => {
      const isActive = button === activeButton;

      const { id, messageId, messageText, disabled, link, messageValues, dataTestId, action, tooltip, icon, messageIcon } =
        button;
      const buttonClasses = cx(classes.button, isActive && classes.activeButton, disabled && classes.disabled);

      const message =
        messageId || messageText ? (
          <Typography>{messageId ? <FormattedMessage id={messageId} values={messageValues} /> : messageText}</Typography>
        ) : null;

      const buttonComponent = link ? (
        <MuiButton data-test-id={dataTestId} key={id} component={Link} to={link} className={buttonClasses} startIcon={icon}>
          {messageIcon}
          {message}
        </MuiButton>
      ) : (
        <MuiButton
          data-test-id={dataTestId}
          key={id}
          disableRipple={disabled}
          className={buttonClasses}
          onClick={disabled ? null : action}
          startIcon={icon}
        >
          {messageIcon}
          {message}
        </MuiButton>
      );

      return tooltip ? (
        <Tooltip key={id} title={<FormattedMessage id={tooltip} />}>
          {buttonComponent}
        </Tooltip>
      ) : (
        buttonComponent
      );
    });

  return <MuiButtonGroup fullWidth={fullWidth}>{renderButtons()}</MuiButtonGroup>;
};

export default ButtonGroup;
