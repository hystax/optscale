import React from "react";
import Box from "@mui/material/Box";
import InputAdornment from "@mui/material/InputAdornment";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import UpdateCostModelWarning from "components/UpdateCostModelWarning/UpdateCostModelWarning";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { MAX_INT_32, COST_MODEL_TYPES } from "utils/constants";
import { isPositiveNumberOrZero, costModelValueMaxFractionDigitsValidation } from "utils/validation";
import useStyles from "./CostModelForm.styles";

const CPU_HOUR_INPUT_NAME = "cpuHour";
const MEMORY_HOUR_INPUT_NAME = "memoryMbHour";

// TODO: We need to check the "number" type in the Mozilla firefox browser, for example. The value is not validated correctly and the string values show a error in the required field.

const CostModelForm = ({ onSubmit, cpuHour, memoryMbHour, isLoading, onCancel }) => {
  const { classes } = useStyles();
  const intl = useIntl();
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm();
  const { currencySymbol } = useOrganizationInfo();

  return (
    <Box>
      <UpdateCostModelWarning costModelType={COST_MODEL_TYPES.K8S} dataTestId="p_recalculation_message" />
      <form
        className={classes.form}
        onSubmit={handleSubmit((data) => {
          onSubmit({
            [CPU_HOUR_INPUT_NAME]: Number(data[CPU_HOUR_INPUT_NAME]),
            [MEMORY_HOUR_INPUT_NAME]: Number(data[MEMORY_HOUR_INPUT_NAME])
          });
        })}
        noValidate
      >
        <Input
          required
          // type="number"
          error={!!errors[CPU_HOUR_INPUT_NAME]}
          helperText={errors[CPU_HOUR_INPUT_NAME] && errors[CPU_HOUR_INPUT_NAME].message}
          defaultValue={cpuHour || 0}
          InputProps={{
            startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
          }}
          label={<FormattedMessage id="cpuPerHour" />}
          {...register(CPU_HOUR_INPUT_NAME, {
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            },
            min: {
              value: 0,
              message: intl.formatMessage({ id: "moreOrEqual" }, { min: 0 })
            },
            max: {
              value: MAX_INT_32,
              message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
            },
            validate: {
              positiveNumber: (value) => (isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumber" })),
              fractionDigits: costModelValueMaxFractionDigitsValidation
            }
          })}
          dataTestId="input_cpu"
        />
        <Input
          required
          // type="number"
          error={!!errors[MEMORY_HOUR_INPUT_NAME]}
          helperText={errors[MEMORY_HOUR_INPUT_NAME] && errors[MEMORY_HOUR_INPUT_NAME].message}
          defaultValue={memoryMbHour || 0}
          InputProps={{
            startAdornment: <InputAdornment position="start">{currencySymbol}</InputAdornment>
          }}
          label={<FormattedMessage id="memoryPerHour" />}
          {...register(MEMORY_HOUR_INPUT_NAME, {
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            },
            min: {
              value: 0,
              message: intl.formatMessage({ id: "moreOrEqual" }, { min: 0 })
            },
            max: {
              value: MAX_INT_32,
              message: intl.formatMessage({ id: "lessOrEqual" }, { max: MAX_INT_32 })
            },
            validate: {
              positiveNumber: (value) => (isPositiveNumberOrZero(value) ? true : intl.formatMessage({ id: "positiveNumber" })),
              fractionDigits: costModelValueMaxFractionDigitsValidation
            }
          })}
          dataTestId="input_memory"
        />
        <FormButtonsWrapper>
          <ButtonLoader
            isLoading={isLoading}
            variant="contained"
            color="primary"
            messageId="save"
            type="submit"
            loaderDataTestId="loading_btn_save"
            dataTestId="btn_save"
          />
          <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
        </FormButtonsWrapper>
      </form>
    </Box>
  );
};

CostModelForm.propTypes = {
  cpuHour: PropTypes.number.isRequired,
  memoryMbHour: PropTypes.number.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default CostModelForm;
