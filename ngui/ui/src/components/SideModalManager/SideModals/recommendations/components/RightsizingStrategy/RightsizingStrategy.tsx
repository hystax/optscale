import { Box, FormHelperText, Input, Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";
import TypographyLoader from "components/TypographyLoader";
import { intl as rawIntl } from "translations/react-intl-config";
import { RIGHTSIZING_METRIC_LIMIT_TYPES } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";
import { isNumberInRange } from "utils/validation";

export const NAME = "rightsizingStrategy";

const THRESHOLD_DAYS_RANGE = Object.freeze({ min: 1, max: 180 });

export const STRATEGIES = Object.freeze({
  OPTIMAL: "optimal",
  SAFE: "safe",
  AGGRESSIVE: "aggressive",
  CUSTOM: "custom"
});

export const STRATEGY_METRICS = Object.freeze({
  [STRATEGIES.OPTIMAL]: {
    type: RIGHTSIZING_METRIC_LIMIT_TYPES.Q99,
    limit: 80
  },
  [STRATEGIES.SAFE]: {
    type: RIGHTSIZING_METRIC_LIMIT_TYPES.MAX,
    limit: 80
  },
  [STRATEGIES.AGGRESSIVE]: {
    type: RIGHTSIZING_METRIC_LIMIT_TYPES.AVG,
    limit: 80
  }
});

const getMetricLimitMessageId = (limitType) =>
  ({
    [RIGHTSIZING_METRIC_LIMIT_TYPES.Q99]: "99quantile",
    [RIGHTSIZING_METRIC_LIMIT_TYPES.MAX]: "maximum",
    [RIGHTSIZING_METRIC_LIMIT_TYPES.AVG]: "average"
  })[limitType];

export const thresholdValidationRules = Object.freeze({
  maxThresholdValidation: ({ metric }) => {
    const limit = Number(metric.limit);

    return Number(limit) > 100 ? rawIntl.formatMessage({ id: "rightsizingLimitMaxValue" }) : true;
  },
  minThresholdValidation: ({ metric }) => {
    const limit = Number(metric.limit);

    return Number(limit) < 0 ? rawIntl.formatMessage({ id: "rightsizingThresholdMinValue" }) : true;
  },
  positiveIntegerNumber: ({ metric }) => {
    const limit = Number(metric.limit);

    return Number.isInteger(limit) ? true : rawIntl.formatMessage({ id: "rightsizingLimitIntegerValue" });
  },
  daysThresholdRange: ({ daysThreshold }) => {
    // TODO: apply granular validations, mixed in one validation function (to show user one alert message instead of changing it every time user changes input) after form won't be "inlined" anymore
    const isInteger = Number.isInteger(daysThreshold);
    const isInRange = isNumberInRange(Number(daysThreshold), THRESHOLD_DAYS_RANGE.min, THRESHOLD_DAYS_RANGE.max);

    return isInteger && isInRange ? true : rawIntl.formatMessage({ id: "daysParameterShouldBeInRange" }, THRESHOLD_DAYS_RANGE);
  }
});

const RightsizingStrategy = ({
  daysThreshold,
  metric,
  strategy,
  onStrategyChange,
  onCustomMetricChange,
  onDaysThresholdChange,
  customMetric,
  isLoading = false,
  error = {}
}) => {
  const intl = useIntl();

  const strategyValuesMessageValues =
    strategy === STRATEGIES.CUSTOM
      ? {
          type: (
            <Selector
              id="custom-strategy-cpu-usage-selector"
              variant="standard"
              value={customMetric.type}
              onChange={(value) => {
                onCustomMetricChange("type", value);
              }}
              sx={{
                margin: "-2px 0px 0px 0px",
                minWidth: "32px",
                marginRight: 0
              }}
            >
              {Object.values(STRATEGY_METRICS).map(({ type }) => (
                <Item key={type} value={type}>
                  <ItemContent>{intl.formatMessage({ id: getMetricLimitMessageId(type) }).toLowerCase()}</ItemContent>
                </Item>
              ))}
            </Selector>
          ),
          limit: (
            <Input
              type="number"
              style={{ margin: 0, maxWidth: "60px" }}
              inputProps={{ style: { padding: "0", textAlign: "center" } }}
              value={customMetric.limit}
              onChange={(event) => {
                const { value } = event.target;
                onCustomMetricChange("limit", Math.abs(value));
              }}
              endAdornment={"%"}
              error={Object.keys(thresholdValidationRules).includes(error.type)}
            />
          )
        }
      : {
          type: metric.type,
          limit: <strong>{`${metric.limit}%`}</strong>,
          strong: (chunks) => <strong>{chunks}</strong>
        };

  return (
    <Box>
      <Typography gutterBottom>
        <FormattedMessage id="rightsizingStrategyDescription" />
      </Typography>
      <Selector
        id="strategy-selector"
        labelMessageId="strategy"
        value={strategy}
        isLoading={isLoading}
        onChange={(value) => {
          onStrategyChange(value);
        }}
      >
        <Item value={STRATEGIES.OPTIMAL}>
          <ItemContent>
            <FormattedMessage id="optimal" />
          </ItemContent>
        </Item>
        <Item value={STRATEGIES.SAFE}>
          <ItemContent>
            <FormattedMessage id="safe" />
          </ItemContent>
        </Item>
        <Item value={STRATEGIES.AGGRESSIVE}>
          <ItemContent>
            <FormattedMessage id="aggressive" />
          </ItemContent>
        </Item>
        <Item value={STRATEGIES.CUSTOM}>
          <ItemContent>
            <FormattedMessage id="custom" />
          </ItemContent>
        </Item>
      </Selector>
      {isLoading ? (
        <TypographyLoader />
      ) : (
        <>
          <Typography component="div">
            <FormattedMessage id="rightsizingStrategyValuesDescription" values={strategyValuesMessageValues} />
          </Typography>
          <Typography component="div">
            <FormattedMessage
              id="rightsizingDaysThreshold"
              values={{
                daysThresholdValue: daysThreshold,
                daysThreshold: (
                  <Input
                    type="number"
                    style={{ margin: 0, maxWidth: "40px" }}
                    inputProps={{ style: { padding: "0", textAlign: "center" } }}
                    value={daysThreshold}
                    onChange={(event) => onDaysThresholdChange(Number(event.target.value))}
                  />
                )
              }}
            />
          </Typography>
        </>
      )}
      {!isEmptyObject(error) && <FormHelperText error>{error.message}</FormHelperText>}
    </Box>
  );
};

export default RightsizingStrategy;
