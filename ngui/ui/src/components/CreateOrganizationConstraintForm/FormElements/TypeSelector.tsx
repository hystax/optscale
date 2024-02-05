import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";
import { ANOMALY_TYPES, QUOTAS_AND_BUDGETS_TYPES, TAGGING_POLICY_TYPES } from "utils/constants";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";

const FIELD_NAME = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TYPE;

const TypeSelector = ({ types }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Controller
      name="type"
      dataTestId={`selector_${FIELD_NAME}`}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: controllerField }) => (
        <Selector
          id="type-selector"
          fullWidth
          required
          error={!!errors[FIELD_NAME]}
          helperText={errors[FIELD_NAME]?.message}
          labelMessageId="type"
          {...controllerField}
        >
          {types.map((type) => (
            <Item key={type} value={type}>
              <ItemContent>
                {intl.formatMessage({
                  id: ANOMALY_TYPES[type] || QUOTAS_AND_BUDGETS_TYPES[type] || TAGGING_POLICY_TYPES[type]
                })}
              </ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default TypeSelector;
