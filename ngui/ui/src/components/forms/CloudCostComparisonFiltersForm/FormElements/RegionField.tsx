import { useIntl } from "react-intl";
import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { FIELD_NAMES, REGIONS } from "../constants";

const FIELD_NAME = FIELD_NAMES.REGION;

const RegionField = () => {
  const intl = useIntl();

  return (
    <Selector
      name={FIELD_NAME}
      required
      fullWidth
      labelMessageId="region"
      items={[
        {
          name: "region.af",
          value: REGIONS.AF
        },
        {
          name: "region.ap",
          value: REGIONS.AP
        },
        {
          name: "region.ca",
          value: REGIONS.CA
        },
        {
          name: "region.eu",
          value: REGIONS.EU
        },
        {
          name: "region.me",
          value: REGIONS.ME
        },
        {
          name: "region.sa",
          value: REGIONS.SA
        },
        {
          name: "region.us",
          value: REGIONS.US
        }
      ].map(({ name, value }) => ({
        value,
        content: <ItemContent>{intl.formatMessage({ id: name })}</ItemContent>
      }))}
    />
  );
};

export default RegionField;
