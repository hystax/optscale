import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import { POOL_TYPES } from "utils/constants";

type PoolTypeIconTooltipContentProps = {
  type: keyof typeof POOL_TYPES;
};

const PoolTypeIconTooltipContent = ({ type }: PoolTypeIconTooltipContentProps) => (
  <KeyValueLabel messageId="type" value={<FormattedMessage id={POOL_TYPES[type]} />} />
);

export default PoolTypeIconTooltipContent;
