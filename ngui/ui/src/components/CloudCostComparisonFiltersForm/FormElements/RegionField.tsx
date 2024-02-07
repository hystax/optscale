import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";

export const FIELD_NAME = "region";

export const REGIONS = Object.freeze({
  AP: "ap",
  EU: "eu",
  CA: "ca",
  SA: "sa",
  US: "us",
  AF: "af",
  ME: "me"
});

const RegionField = () => {
  const intl = useIntl();

  const { control } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      render={({ field }) => (
        <Selector id="region-select" fullWidth required labelMessageId="region" {...field}>
          {[
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
          ].map(({ name, value }) => (
            <Item key={value} value={value}>
              <ItemContent>{intl.formatMessage({ id: name })}</ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default RegionField;
