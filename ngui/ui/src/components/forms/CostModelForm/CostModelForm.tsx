import { FormProvider, useForm } from "react-hook-form";
import UpdateCostModelWarning from "components/UpdateCostModelWarning/UpdateCostModelWarning";
import { COST_MODEL_TYPES } from "utils/constants";
import useStyles from "./CostModelForm.styles";
import { CpuPerHourField, FormButtons, MemoryPerHourField } from "./FormElements";
import { CostModelFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

const CostModelForm = ({ cpuHour, memoryMbHour, onSubmit, onCancel, isLoading = false }: CostModelFormProps) => {
  const { classes } = useStyles();

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      cpuHour,
      memoryMbHour
    })
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form className={classes.form} onSubmit={handleSubmit(onSubmit)} noValidate>
        <UpdateCostModelWarning costModelType={COST_MODEL_TYPES.K8S} dataTestId="p_recalculation_message" />
        <CpuPerHourField />
        <MemoryPerHourField />
        <FormButtons onCancel={onCancel} isLoading={isLoading} />
      </form>
    </FormProvider>
  );
};

export default CostModelForm;
