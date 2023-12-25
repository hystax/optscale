import { useState } from "react";
import { useTheme } from "@emotion/react";
import { Slider, SliderMark } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";
import { intl } from "translations/react-intl-config";
import { formatSecondsToHHMMSS } from "utils/datetime";

export const formatToChartTime = (x) => formatSecondsToHHMMSS(Number(x));

const CustomMarkComponent = (props) => {
  const theme = useTheme();

  const { children, className, "data-index": dataIndex, milestones, ...other } = props;
  const [markTooltipText, setMarkTooltipText] = useState();

  const getMarkTooltipText = () => {
    const text = milestones[dataIndex][1]?.map((milestone) => <div key={milestone}>{milestone}</div>);
    setMarkTooltipText(text);
  };

  return (
    <Tooltip title={markTooltipText} placement="top">
      <SliderMark
        sx={{
          height: 8,
          width: 8,
          border: `1px solid ${theme.palette.common.white}`,
          borderRadius: "50%",
          backgroundColor: "currentColor",
          opacity: 0.38,
          "&.MuiSlider-markActive": {
            opacity: 1,
            backgroundColor: theme.palette.primary.dark
          }
        }}
        onMouseEnter={() => getMarkTooltipText()}
        className={className}
        {...other}
      />
    </Tooltip>
  );
};

const TimerangeSlider = ({ milestonesGroupedByTimeTuples, selectedSegment, setSelectedSegment, xValuesRange }) => {
  const getSelectedSegment = () => selectedSegment ?? xValuesRange;

  const [fromFormatted, toFormatted] = getSelectedSegment().map(formatToChartTime);
  const chartsTimerangeMessage = intl.formatMessage({ id: "timerange" }, { from: fromFormatted, to: toFormatted });

  const sliderMarks = milestonesGroupedByTimeTuples.map(([value]) => ({ value }));

  return (
    <Slider
      slots={{
        mark: CustomMarkComponent
      }}
      slotProps={{
        mark: { milestones: milestonesGroupedByTimeTuples }
      }}
      marks={sliderMarks}
      getAriaLabel={() => chartsTimerangeMessage}
      value={selectedSegment || xValuesRange}
      valueLabelDisplay="off"
      min={xValuesRange[0]}
      max={xValuesRange[1]}
      onChange={(_, segment) => {
        let [a, b] = segment;
        a = a === b && b === xValuesRange[1] ? Math.max(xValuesRange[0], a - 1) : a;
        b = a === b && b !== xValuesRange[1] ? Math.min(xValuesRange[1], a + 1) : b;
        setSelectedSegment([a, b]);
      }}
      getAriaValueText={() => chartsTimerangeMessage}
      valueLabelFormat={(value, index) => {
        const messageId = index === 0 ? "fromX" : "toX";
        return <FormattedMessage id={messageId} values={{ value: formatToChartTime(value) }} />;
      }}
    />
  );
};

export default TimerangeSlider;
