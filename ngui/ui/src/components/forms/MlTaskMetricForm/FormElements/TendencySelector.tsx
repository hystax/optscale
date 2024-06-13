import { useIntl } from "react-intl";
import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { GOALS_FILTER_TYPES } from "utils/constants";
import { FIELD_NAMES } from "../constants";

const FIELD_MESSAGE_ID = "tendency";

const FIELD_NAME = FIELD_NAMES.TENDENCY;

const TendencySelector = ({ isLoading = false }) => {
  const intl = useIntl();

  return (
    <Selector
      name={FIELD_NAME}
      id="tendency-selector"
      fullWidth
      required
      labelMessageId={FIELD_MESSAGE_ID}
      isLoading={isLoading}
      items={[
        {
          value: GOALS_FILTER_TYPES.LESS_IS_BETTER,
          content: <ItemContent>{intl.formatMessage({ id: "lessIsBetter" })}</ItemContent>
        },
        {
          value: GOALS_FILTER_TYPES.MORE_IS_BETTER,
          content: <ItemContent>{intl.formatMessage({ id: "moreIsBetter" })}</ItemContent>
        }
      ]}
    />
  );
};

export default TendencySelector;
