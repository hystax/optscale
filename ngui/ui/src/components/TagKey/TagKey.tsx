import { FormattedMessage } from "react-intl";

const TagKey = ({ tagKey }) => (tagKey === null ? <FormattedMessage id="(untagged)" /> : tagKey);

export default TagKey;
