import { Autocomplete, FormControl, Typography, createFilterOptions } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import localeManager from "translations/react-intl-config";
import { FIELD_NAMES } from "../constants";

const ZONES_BLACKLIST = [
  /**
   * This timezone is not supported by pytz 2023.3.post1
   * Exclude it to ensure compatibility with the backend
   */
  "Factory"
];

const SUPPORTED_TIME_ZONES = Intl.supportedValuesOf("timeZone").filter((zone) => !ZONES_BLACKLIST.includes(zone));

const TIME_ZONE_NAMES = Object.fromEntries(
  SUPPORTED_TIME_ZONES.map((zone) => {
    const shortOffsetZoneName = Intl.DateTimeFormat(localeManager.locale, {
      timeZoneName: "shortOffset",
      timeZone: zone
    })
      .formatToParts()
      .find((i) => i.type === "timeZoneName").value;

    const longGenericZoneName = Intl.DateTimeFormat(localeManager.locale, {
      timeZoneName: "longGeneric",
      timeZone: zone
    })
      .formatToParts()
      .find((i) => i.type === "timeZoneName").value;

    return [
      zone,
      {
        shortOffsetZoneName,
        longGenericZoneName
      }
    ];
  })
);

const getTimeZoneString = (timeZone) => {
  const { shortOffsetZoneName, longGenericZoneName } = TIME_ZONE_NAMES[timeZone];

  return [timeZone, shortOffsetZoneName, longGenericZoneName].join(" ");
};

const TimeZoneField = ({ name = FIELD_NAMES.TIME_ZONE }) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <FormControl fullWidth>
      <Controller
        name={name}
        control={control}
        rules={{
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          validate: {
            allowedTimeZone: (value) =>
              SUPPORTED_TIME_ZONES.includes(value) ? true : intl.formatMessage({ id: "invalidTimeZone" })
          }
        }}
        render={({ field }) => {
          const { name: fieldName, onBlur, value, onChange, ref } = field;

          return (
            <Autocomplete
              name={fieldName}
              freeSolo
              disableClearable
              clearOnEscape
              selectOnFocus
              value={value}
              options={SUPPORTED_TIME_ZONES}
              onInputChange={(event, selected) => {
                onChange(selected);
              }}
              onBlur={onBlur}
              filterOptions={createFilterOptions({
                matchFrom: "any",
                stringify: (timeZone) => getTimeZoneString(timeZone)
              })}
              renderOption={(props, timeZone) => {
                const { shortOffsetZoneName, longGenericZoneName } = TIME_ZONE_NAMES[timeZone];

                return (
                  <li {...props}>
                    <div>
                      <Typography variant="body2">{timeZone}</Typography>
                      <Typography variant="caption">{`${longGenericZoneName} (${shortOffsetZoneName})`}</Typography>
                    </div>
                  </li>
                );
              }}
              renderInput={(params) => (
                <Input
                  {...params}
                  ref={ref}
                  margin="none"
                  error={!!errors[fieldName]}
                  helperText={errors[fieldName]?.message}
                  label={<FormattedMessage id="timeZone" />}
                  required
                />
              )}
            />
          );
        }}
      />
    </FormControl>
  );
};

export default TimeZoneField;
