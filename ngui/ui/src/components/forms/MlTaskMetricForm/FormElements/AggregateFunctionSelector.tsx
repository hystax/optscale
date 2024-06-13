import { useIntl } from "react-intl";
import { AGGREGATE_FUNCTION, AGGREGATE_FUNCTION_MESSAGE_ID } from "components/AggregateFunctionFormattedMessage";
import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { FIELD_NAMES } from "../constants";

const FIELD_MESSAGE_ID = "aggregateFunction";

const FIELD_NAME = FIELD_NAMES.FUNCTION;

const AggregateFunctionSelector = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <Selector
      name={FIELD_NAME}
      fullWidth
      required
      id="aggregate-function-selector"
      labelMessageId={FIELD_MESSAGE_ID}
      isLoading={isLoading}
      items={Object.values(AGGREGATE_FUNCTION).map((aggregateFunction) => ({
        value: aggregateFunction,
        content: <ItemContent>{intl.formatMessage({ id: AGGREGATE_FUNCTION_MESSAGE_ID[aggregateFunction] })}</ItemContent>
      }))}
    />
  );
};

export default AggregateFunctionSelector;
