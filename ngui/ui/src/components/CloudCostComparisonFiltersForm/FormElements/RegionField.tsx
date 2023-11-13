import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { makeStyles } from "tss-react/mui";
import Selector from "components/Selector";

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

const useStyles = makeStyles()(() => ({
  selector: {
    marginRight: 0
  }
}));

const RegionField = () => {
  const intl = useIntl();

  const { control } = useFormContext();

  const { classes } = useStyles();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      render={({ field }) => (
        <Selector
          customClass={classes.selector}
          fullWidth
          required
          data={{
            items: [
              {
                name: intl.formatMessage({ id: "region.af" }),
                value: REGIONS.AF
              },
              {
                name: intl.formatMessage({ id: "region.ap" }),
                value: REGIONS.AP
              },
              {
                name: intl.formatMessage({ id: "region.ca" }),
                value: REGIONS.CA
              },
              {
                name: intl.formatMessage({ id: "region.eu" }),
                value: REGIONS.EU
              },
              {
                name: intl.formatMessage({ id: "region.me" }),
                value: REGIONS.ME
              },
              {
                name: intl.formatMessage({ id: "region.sa" }),
                value: REGIONS.SA
              },
              {
                name: intl.formatMessage({ id: "region.us" }),
                value: REGIONS.US
              }
            ]
          }}
          labelId="region"
          {...field}
        />
      )}
    />
  );
};

export default RegionField;
