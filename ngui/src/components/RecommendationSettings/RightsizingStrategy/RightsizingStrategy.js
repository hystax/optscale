import React from "react";
import { Box, FormHelperText, Input, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";
import TypographyLoader from "components/TypographyLoader";
import { intl as rawIntl } from "translations/react-intl-config";
import { RIGHTSIZING_METRIC_LIMIT_TYPES } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";
import useStyles from "./RightsizingStrategy.styles";

export const NAME = "rightsizingStrategy";

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
  }[limitType]);

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
  }
});

const RightsizingStrategy = ({
  metric,
  strategy,
  onStrategyChange,
  onCustomMetricChange,
  customMetric,
  isLoading = false,
  error = {}
}) => {
  const intl = useIntl();

  const { classes } = useStyles();

  const strategyValuesMessageValues =
    strategy === STRATEGIES.CUSTOM
      ? {
          type: (
            <Selector
              customClass={classes.customSelectorStyles}
              data={{
                items: Object.values(STRATEGY_METRICS).map(({ type }) => ({
                  name: intl.formatMessage({ id: getMetricLimitMessageId(type) }).toLowerCase(),
                  value: type
                }))
              }}
              sx={{
                // align inline selector with a formatted text
                margin: "-2px 0px 0px 0px"
              }}
              variant="standard"
              value={customMetric.type}
              onChange={(value) => {
                onCustomMetricChange("type", value);
              }}
            />
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
      {isLoading ? (
        <SelectorLoader readOnly labelId="strategy" />
      ) : (
        <Selector
          data={{
            items: [
              {
                name: <FormattedMessage id="optimal" />,
                value: STRATEGIES.OPTIMAL
              },
              {
                name: <FormattedMessage id="safe" />,
                value: STRATEGIES.SAFE
              },
              {
                name: <FormattedMessage id="aggressive" />,
                value: STRATEGIES.AGGRESSIVE
              },
              {
                name: <FormattedMessage id="custom" />,
                value: STRATEGIES.CUSTOM
              }
            ]
          }}
          labelId="strategy"
          value={strategy}
          onChange={(value) => {
            onStrategyChange(value);
          }}
        />
      )}

      {isLoading ? (
        <TypographyLoader />
      ) : (
        <Typography component="div">
          <FormattedMessage id="rightsizingStrategyValuesDescription" values={strategyValuesMessageValues} />
        </Typography>
      )}
      {!isEmptyObject(error) && <FormHelperText error>{error.message}</FormHelperText>}
    </Box>
  );
};

const metricPropTypes = PropTypes.shape({
  type: PropTypes.oneOf(Object.values(RIGHTSIZING_METRIC_LIMIT_TYPES)).isRequired,
  limit: PropTypes.number.isRequired
}).isRequired;

RightsizingStrategy.propTypes = {
  metric: metricPropTypes,
  customMetric: metricPropTypes,
  strategy: PropTypes.oneOf(Object.values(STRATEGIES)).isRequired,
  onStrategyChange: PropTypes.func.isRequired,
  onCustomMetricChange: PropTypes.func.isRequired,
  error: PropTypes.object,
  isLoading: PropTypes.bool
};

export default RightsizingStrategy;
