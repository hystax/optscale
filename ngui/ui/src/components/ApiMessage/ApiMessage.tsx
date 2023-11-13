import { FormattedMessage } from "react-intl";

// Converts an array into an object the following way:
// ["item1", "item2"] => {"0": "item1", "1": "item2"}
const buildMessageValues = (items) => Object.fromEntries(items.map((item, index) => [index, item]));

const ApiMessage = ({ code, params = [], defaultMessage = "" }) => (
  <FormattedMessage id={code} values={buildMessageValues(params)} defaultMessage={defaultMessage} />
);

export default ApiMessage;
