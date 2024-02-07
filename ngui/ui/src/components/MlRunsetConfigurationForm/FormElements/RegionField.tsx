import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContentWithDataSourceIcon } from "components/Selector";

export const FIELD_NAME = "region";

const LABEL_ID = "region";

const RegionField = ({ regions, isLoading = false }) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field }) => (
        <Selector
          id="region-selector"
          fullWidth
          required
          isLoading={isLoading}
          error={!!errors[FIELD_NAME]}
          helperText={errors?.[FIELD_NAME]?.message}
          labelMessageId={LABEL_ID}
          {...field}
        >
          {regions.map(({ name, cloud_type: dataSourceType }) => (
            <Item key={name} value={name}>
              <ItemContentWithDataSourceIcon dataSourceType={dataSourceType}>{name}</ItemContentWithDataSourceIcon>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default RegionField;
