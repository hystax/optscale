import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";

const MlEditModelFormOwnerField = ({ name, employees = [], isLoading = false }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Controller
      name={name}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field }) => (
        <Selector
          id="owner-selector"
          fullWidth
          required
          error={!!errors[name]}
          helperText={errors?.[name]?.message}
          labelMessageId="owner"
          isLoading={isLoading}
          {...field}
        >
          {employees.map(({ id, name: employeeName }) => (
            <Item key={id} value={id}>
              <ItemContent>{employeeName}</ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default MlEditModelFormOwnerField;
