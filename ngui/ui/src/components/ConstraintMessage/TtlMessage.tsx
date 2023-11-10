import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import { CONSTRAINT_MESSAGE_FORMAT } from "utils/constraints";
import { format, secondsToMilliseconds, EN_FULL_FORMAT } from "utils/datetime";

const TtlMessage = ({ type, limit, formats = {} }) => {
  const { ttl: ttlFormat = CONSTRAINT_MESSAGE_FORMAT.DATETIME } = formats;

  if (ttlFormat === CONSTRAINT_MESSAGE_FORMAT.TEXT) {
    return <FormattedMessage values={{ value: limit }} id="hour" />;
  }
  if (ttlFormat === CONSTRAINT_MESSAGE_FORMAT.DATETIME) {
    return format(secondsToMilliseconds(limit), EN_FULL_FORMAT);
  }
  if (ttlFormat === CONSTRAINT_MESSAGE_FORMAT.EXPIRES_AT_DATETIME) {
    return (
      <KeyValueLabel
        isBoldValue={false}
        messageId="expiresAt"
        value={format(secondsToMilliseconds(limit), EN_FULL_FORMAT)}
        dataTestIds={{
          key: `p_${type}_expires_at`,
          value: `p_${type}_expires_at_value`
        }}
      />
    );
  }
  return null;
};

export default TtlMessage;
