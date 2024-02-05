import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContentWithDataSourceIcon } from "components/Selector";

export const FIELD_NAME = "instanceType";

const LABEL_ID = "instanceType";

const InstanceTypeField = ({ instanceTypes, isLoading = false }) => {
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
          id="instance-type-selector"
          fullWidth
          required
          error={!!errors[FIELD_NAME]}
          helperText={errors?.[FIELD_NAME]?.message}
          labelMessageId={LABEL_ID}
          isLoading={isLoading}
          {...field}
        >
          {instanceTypes.map(({ name, cloud_type: dataSourceType }) => (
            <Item key={name} value={name}>
              <ItemContentWithDataSourceIcon dataSourceType={dataSourceType}>{name}</ItemContentWithDataSourceIcon>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default InstanceTypeField;
