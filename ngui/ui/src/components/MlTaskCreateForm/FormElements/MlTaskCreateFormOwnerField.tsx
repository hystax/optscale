import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";

const MlTaskCreateFormOwnerField = ({ name, employees = [], isLoading = false }) => {
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
          {employees.map((employee) => (
            <Item key={employee.id} value={employee.id}>
              <ItemContent>{employee.name}</ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default MlTaskCreateFormOwnerField;
