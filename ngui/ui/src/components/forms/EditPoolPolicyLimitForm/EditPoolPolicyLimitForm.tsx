import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import Box from "@mui/material/Box";
import { FormProvider, useForm } from "react-hook-form";
import IconButton from "components/IconButton";
import { isExpensesLimit, isTtlLimit } from "utils/constraints";
import { ExpenseLimitField, TtlLimitField } from "./FormElements";
import { EditPoolPolicyLimitFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const getInputByType = (type) => {
  if (isExpensesLimit(type)) {
    return <ExpenseLimitField />;
  }
  if (isTtlLimit(type)) {
    return <TtlLimitField />;
  }
  return null;
};

const EditPoolPolicyLimitForm = ({
  policyType,
  policyLimit,
  onSubmit,
  onCancel,
  isLoading = false
}: EditPoolPolicyLimitFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues(policyLimit)
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Box display="flex">
          <Box>{getInputByType(policyType)}</Box>
          <Box display="flex" height="max-content">
            <IconButton isLoading={isLoading} icon={<CheckOutlinedIcon />} type="submit" dataTestId={`btn_${policyType}_ok`} />
            <IconButton icon={<CloseIcon />} onClick={onCancel} dataTestId={`btn_${policyType}_cancel`} />
          </Box>
        </Box>
      </form>
    </FormProvider>
  );
};

export default EditPoolPolicyLimitForm;
