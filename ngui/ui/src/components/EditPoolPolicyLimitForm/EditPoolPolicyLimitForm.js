import React from "react";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import IconButton from "components/IconButton";
import { isExpensesLimit, isTtlLimit } from "utils/constraints";
import { EditPoolPolicyLimitFormExpenseLimitInput, EditPoolPolicyLimitFormTtlLimitInput } from "./FormElements";

const getInputByType = ({ type, defaultValue }) => {
  if (isExpensesLimit(type)) {
    return <EditPoolPolicyLimitFormExpenseLimitInput name="limit" defaultValue={defaultValue} margin="none" />;
  }
  if (isTtlLimit(type)) {
    return <EditPoolPolicyLimitFormTtlLimitInput name="limit" defaultValue={defaultValue} margin="none" />;
  }
  return null;
};

const EditPoolPolicyLimitForm = ({ onSubmit, policyType, policyLimit, isLoading, onCancel }) => {
  const methods = useForm();

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Box display="flex">
          <Box>
            {getInputByType({
              type: policyType,
              defaultValue: policyLimit
            })}
          </Box>
          <Box display="flex" height="max-content">
            <IconButton isLoading={isLoading} icon={<CheckOutlinedIcon />} type="submit" dataTestId={`btn_${policyType}_ok`} />
            <IconButton icon={<CloseIcon />} onClick={onCancel} dataTestId={`btn_${policyType}_cancel`} />
          </Box>
        </Box>
      </form>
    </FormProvider>
  );
};

EditPoolPolicyLimitForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  policyType: PropTypes.string.isRequired,
  policyLimit: PropTypes.number.isRequired,
  isLoading: PropTypes.bool
};

export default EditPoolPolicyLimitForm;
