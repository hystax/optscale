import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";

export const FIELD_NAME = "task";

const LABEL_ID = "task";

const TaskField = ({ tasks, isLoading }) => {
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
          id="task-selector"
          fullWidth
          required
          error={!!errors[FIELD_NAME]}
          helperText={errors?.[FIELD_NAME]?.message}
          labelMessageId={LABEL_ID}
          isLoading={isLoading}
          {...field}
        >
          {tasks.map(({ id, name }) => (
            <Item key={id} value={id}>
              <ItemContent>{name}</ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default TaskField;
