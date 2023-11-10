import { FormattedMessage } from "react-intl";

const TrafficFromToLabel = ({ from, to }) => (
  <FormattedMessage
    id="filterFromTo"
    values={{
      from,
      to,
      strong: (chunks) => <strong>{chunks}</strong>
    }}
  />
);

export default TrafficFromToLabel;
