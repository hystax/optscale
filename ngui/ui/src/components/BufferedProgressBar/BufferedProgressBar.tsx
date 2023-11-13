import Box from "@mui/material/Box";
import LinearProgress from "@mui/material/LinearProgress";
import CircleLabel from "components/CircleLabel";
import Tooltip from "components/Tooltip";
import useStyles from "./BufferedProgressBar.styles";

const BufferedProgressBar = ({
  value,
  valueBuffer = 0,
  width = "auto",
  valueColor,
  valueBufferColor,
  totalColor,
  tooltip = {},
  dataTestId
}) => {
  const { classes, cx } = useStyles({ mainColor: valueColor, secondaryColor: valueBufferColor, backgroundColor: totalColor });

  const {
    show: showTooltip = false,
    valueTooltipMessage = "",
    valueBufferTooltipMessage = "",
    totalTooltipMessage = "",
    customTooltipMessage = "",
    placement = "top"
  } = tooltip;

  const renderProgress = () => (
    <Box className={classes.wrapper} width={width}>
      <LinearProgress
        data-test-id={dataTestId}
        className={cx(classes.progress)}
        classes={{
          bar1Buffer: classes.bar1Buffer,
          bar2Buffer: classes.bar2Buffer,
          dashed: classes.dashed
        }}
        variant={"buffer"}
        value={Math.min(value, 100)}
        valueBuffer={valueBuffer}
      />
    </Box>
  );

  const renderTooltip = () => (
    <>
      {valueTooltipMessage && <CircleLabel figureColor={valueColor} label={valueTooltipMessage} textFirst={false} />}
      {valueBufferTooltipMessage && (
        <CircleLabel figureColor={valueBufferColor} label={valueBufferTooltipMessage} textFirst={false} />
      )}
      {totalTooltipMessage && <CircleLabel figureColor={totalColor} label={totalTooltipMessage} textFirst={false} />}
      {customTooltipMessage}
    </>
  );

  return showTooltip ? (
    <Tooltip title={renderTooltip()} placement={placement}>
      {renderProgress()}
    </Tooltip>
  ) : (
    renderProgress()
  );
};

export default BufferedProgressBar;
