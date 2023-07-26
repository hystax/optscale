import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";

export const AGGREGATE_FUNCTION = Object.freeze({
  LAST: "last",
  SUM: "sum",
  MAX: "max",
  AVERAGE: "avg"
});

export const AGGREGATE_FUNCTION_MESSAGE_ID = Object.freeze({
  [AGGREGATE_FUNCTION.LAST]: "last",
  [AGGREGATE_FUNCTION.SUM]: "sum",
  [AGGREGATE_FUNCTION.MAX]: "max",
  [AGGREGATE_FUNCTION.AVERAGE]: "average"
});

const AggregateFunctionFormattedMessage = ({ aggregateFunction }) => (
  <FormattedMessage id={AGGREGATE_FUNCTION_MESSAGE_ID[aggregateFunction]} />
);

AggregateFunctionFormattedMessage.propTypes = {
  aggregateFunction: PropTypes.oneOf(Object.values(AGGREGATE_FUNCTION)).isRequired
};

export default AggregateFunctionFormattedMessage;
