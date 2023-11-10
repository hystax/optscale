import { Grid } from "@mui/material";
import HeartLineChart, { DEFAULT_COLORS } from "components/HeartLineChart";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/HeartLineChart`,
  argTypes: {
    debug: {
      name: "Debug",
      control: "boolean"
    },
    values: {
      options: ["Positive", "Negative", "Positive and negative", "All equal"],
      control: { type: "select" },
      defaultValue: "Positive"
    },
    thresholdStart: {
      name: "Threshold area start",
      control: { type: "range", min: -100, max: 100, step: 1 },
      defaultValue: 19
    },
    thresholdEnd: { name: "Threshold area end", control: { type: "range", min: -100, max: 100, step: 1 }, defaultValue: 19 },
    startThresholdColor: {
      name: "Start threshold color",
      control: { type: "color" },
      defaultValue: DEFAULT_COLORS.START_THRESHOLD
    },
    endThresholdColor: {
      name: "End threshold color",
      control: { type: "color" },
      defaultValue: DEFAULT_COLORS.END_THRESHOLD
    }
  }
};

export const basic = (args) => {
  const getValues = () => {
    if (args.values === "Positive") {
      return [10, 10, 12, 12, 14, 14, 16, 16, 18, 18, 20, 20, 22, 22, 24, 24, 26, 26, 28, 28];
    }

    if (args.values === "Negative") {
      return [-10, -10, -12, -12, -14, -14, -16, -16, -18, -18, -20, -20, -22, -22, -24, -24, -26, -26, -28, -28];
    }

    if (args.values === "Positive and negative") {
      return [10, -10, 12, -12, 14, -14, 16, -16, 18, -18, 20, -20, 22, -22, 24, -24, 26, -26, 28, -28];
    }

    if (args.values === "All equal") {
      return [18, 18, 18, 18, 18, 18, 18, 18, 18, 18];
    }

    return [];
  };

  return (
    <HeartLineChart
      values={getValues()}
      width={175}
      height={200}
      thresholdColors={{
        start: args.startThresholdColor,
        end: args.endThresholdColor
      }}
      thresholdArea={{
        start: args.thresholdStart,
        end: args.thresholdEnd
      }}
      debug={args.debug}
    />
  );
};

export const history = ({ args }) => (
  <Grid container spacing={2}>
    <Grid item xs={4}>
      <HeartLineChart
        values={[10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}
        width={175}
        height={200}
        thresholdColors={{
          start: args.startThresholdColor,
          end: args.endThresholdColor
        }}
        thresholdArea={{
          start: args.thresholdStart,
          end: args.thresholdEnd
        }}
        debug={args.debug}
      />
    </Grid>
  </Grid>
);
