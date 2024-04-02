import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import MlTaskMetricForm, { ML_TASK_METRIC_FORM_FIELD_NAMES } from "components/MlTaskMetricForm";
import MlTasksService from "services/MlTasksService";
import { ML_TASK_METRICS } from "urls";

const CreateMlTaskMetricFormContainer = () => {
  const navigate = useNavigate();

  const { useCreateGlobalMetric } = MlTasksService();

  const { onCreate, isLoading } = useCreateGlobalMetric();

  const redirect = () => navigate(ML_TASK_METRICS);

  const onSubmit = (formData) => {
    onCreate(formData).then(() => {
      redirect();
    });
  };

  const onCancel = () => redirect();

  const defaultValues = useMemo(
    () => ({
      [ML_TASK_METRIC_FORM_FIELD_NAMES.NAME]: "",
      [ML_TASK_METRIC_FORM_FIELD_NAMES.KEY]: "",
      [ML_TASK_METRIC_FORM_FIELD_NAMES.TENDENCY]: "",
      [ML_TASK_METRIC_FORM_FIELD_NAMES.TARGET_VALUE]: 0,
      [ML_TASK_METRIC_FORM_FIELD_NAMES.FUNCTION]: ""
    }),
    []
  );

  return <MlTaskMetricForm defaultValues={defaultValues} onSubmit={onSubmit} onCancel={onCancel} isSubmitLoading={isLoading} />;
};

export default CreateMlTaskMetricFormContainer;
