import { FormattedMessage } from "react-intl";

const FromToArrowLabel = ({ from, to, strong = false }) => {
  const label = <FormattedMessage id="value -> value" values={{ value1: from, value2: to }} />;

  return strong ? <strong>{label}</strong> : label;
};

export default FromToArrowLabel;
