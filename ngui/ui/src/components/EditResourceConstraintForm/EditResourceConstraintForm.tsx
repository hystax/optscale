import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import IconButton from "components/IconButton";
import QuickDatePickerValues from "components/QuickDatePickerValues";
import { isExpensesLimit, isTtlLimit } from "utils/constraints";
import { millisecondsToSeconds, secondsToMilliseconds } from "utils/datetime";
import { isEmpty as isEmptyObject } from "utils/objects";
import {
  EditResourceConstraintFormExpenseLimitInput as ExpenseLimitInput,
  EditResourceConstraintFormTtlLimitInput as TtlLimitInput
} from "./FormElements";

const LIMIT_INPUT_NAME = "limit";

const getInputByType = ({ inputName, type, defaultValue }) => {
  if (isExpensesLimit(type)) {
    return <ExpenseLimitInput name={inputName} defaultValue={defaultValue} dataTestId={`input_${type}`} />;
  }
  if (isTtlLimit(type)) {
    return (
      <TtlLimitInput name={inputName} defaultValue={defaultValue === 0 ? undefined : secondsToMilliseconds(defaultValue)} />
    );
  }
  return null;
};

const EditResourceConstraintForm = ({
  constraintType,
  constraintLimit,
  constraintId,
  onSubmit,
  onSuccess,
  onCancel,
  isLoading = false
}) => {
  const methods = useForm();
  const { handleSubmit, setValue, trigger } = methods;

  const submit = (form) => {
    const getNewLimitValue = () => {
      if (isExpensesLimit(constraintType)) {
        return Number(form.limit);
      }
      if (isTtlLimit(constraintType)) {
        return millisecondsToSeconds(Number(form.limit || 0));
      }
      return undefined;
    };

    const newLimitValue = getNewLimitValue();

    if (newLimitValue !== constraintLimit) {
      onSubmit(
        { limit: newLimitValue, policyId: constraintId },
        {
          onSuccess: () => onSuccess()
        }
      );
    } else {
      onSuccess();
    }
  };

  const setLimitInputValue = (newValue) => setValue(LIMIT_INPUT_NAME, newValue);

  const updateLimitInput = (newValue) => {
    setLimitInputValue(newValue);
    trigger(LIMIT_INPUT_NAME, { shouldFocus: true });
  };

  const getQuickValues = (type) => {
    if (isExpensesLimit(type)) {
      return {
        label: "setTo",
        items: [
          {
            label: "noLimit",
            dataTestId: `btn_${type}_no_limit`,
            key: "noLimit",
            onClick: () => updateLimitInput(0)
          }
        ]
      };
    }
    return {};
  };

  const quickValue = getQuickValues(constraintType);

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(submit)} noValidate>
        <Box display="flex">
          <Box>
            {getInputByType({
              inputName: LIMIT_INPUT_NAME,
              type: constraintType,
              defaultValue: constraintLimit
            })}
            {!isEmptyObject(quickValue) && (
              <QuickDatePickerValues titleMessageId={quickValue.label} items={quickValue.items} orItems={quickValue.orItems} />
            )}
          </Box>
          <Box display="flex" height="max-content">
            <IconButton
              isLoading={isLoading}
              dataTestId={`btn_save_${constraintType}`}
              icon={<CheckOutlinedIcon />}
              type="submit"
            />
            <IconButton dataTestId={`btn_close_edit_${constraintType}`} icon={<CloseIcon />} onClick={onCancel} />
          </Box>
        </Box>
      </form>
    </FormProvider>
  );
};

export default EditResourceConstraintForm;
