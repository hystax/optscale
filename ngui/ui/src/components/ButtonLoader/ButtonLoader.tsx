import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Button from "components/Button";
import useStyles from "./ButtonLoader.styles";

const ButtonLoader = ({
  dataTestId,
  dataProductTourId,
  loaderDataTestId,
  messageId,
  disabled,
  startIcon,
  onClick,
  link,
  type,
  size,
  variant,
  customWrapperClass,
  customClass,
  fullWidth,
  download,
  href,
  isLoading = false,
  color = "info",
  uppercase = true,
  tooltip,
  ...rest
}) => {
  const { classes, cx } = useStyles();
  const wrapperClass = cx(classes.wrapper, fullWidth ? classes.wrapperFullWidth : "", customWrapperClass);
  const buttonClass = cx(fullWidth ? classes.buttonFullWidth : "", classes[customClass] || customClass);

  const circularProgressColor = {
    primary: classes.primaryCircularProgressColor,
    success: classes.successCircularProgressColor,
    error: classes.errorCircularProgressColor,
    info: classes.infoCircularProgressColor
  };

  return (
    <Box className={wrapperClass}>
      {isLoading && (
        <CircularProgress
          size={24}
          className={cx(classes.buttonProgress, circularProgressColor[color])}
          data-test-id={loaderDataTestId}
        />
      )}
      <Button
        dataTestId={dataTestId}
        dataProductTourId={dataProductTourId}
        uppercase={uppercase}
        messageId={messageId}
        startIcon={startIcon}
        color={color}
        disabled={disabled || isLoading}
        onClick={onClick}
        link={link}
        href={href}
        download={download}
        type={type}
        size={size}
        variant={variant}
        customClass={buttonClass}
        tooltip={tooltip}
        {...rest}
      />
    </Box>
  );
};

export default ButtonLoader;
