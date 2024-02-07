import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContentWithDataSourceIcon } from "components/Selector";

export const FIELD_NAME = "dataSource";

const LABEL_ID = "dataSource";

const DataSourceField = ({ dataSources, isLoading = false }) => {
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
          id="data-source-selector"
          fullWidth
          required
          error={!!errors[FIELD_NAME]}
          helperText={errors?.[FIELD_NAME]?.message}
          labelMessageId={LABEL_ID}
          isLoading={isLoading}
          {...field}
        >
          {dataSources.map(({ id, name, type }) => (
            <Item key={id} value={id}>
              <ItemContentWithDataSourceIcon dataSourceType={type}>{name}</ItemContentWithDataSourceIcon>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default DataSourceField;
