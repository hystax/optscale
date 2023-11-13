import { FormattedMessage } from "react-intl";
import { useDataSources } from "hooks/useDataSources";

const CloudType = ({ type }) => {
  const { cloudTypeMessageId } = useDataSources(type);

  return cloudTypeMessageId ? <FormattedMessage id={cloudTypeMessageId} /> : type;
};

export default CloudType;
