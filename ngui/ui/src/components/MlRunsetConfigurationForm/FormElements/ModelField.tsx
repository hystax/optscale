import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

export const FIELD_NAME = "model";

const LABEL_ID = "task";

const ModelField = ({ models, isLoading }) => {
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
      render={({ field: { onChange, ...rest } }) =>
        isLoading ? (
          <SelectorLoader readOnly fullWidth labelId={LABEL_ID} isRequired />
        ) : (
          <Selector
            dataTestId="selector_tasks"
            fullWidth
            required
            error={!!errors[FIELD_NAME]}
            helperText={errors?.[FIELD_NAME]?.message}
            data={{
              items: models.map(({ id, name }) => ({
                name,
                value: id
              }))
            }}
            labelId={LABEL_ID}
            onChange={onChange}
            {...rest}
          />
        )
      }
    />
  );
};

export default ModelField;
