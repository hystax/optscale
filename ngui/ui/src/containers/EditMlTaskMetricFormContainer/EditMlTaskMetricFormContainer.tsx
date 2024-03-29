import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MlTaskMetricForm, { ML_TASK_METRIC_FORM_FIELD_NAMES } from "components/MlTaskMetricForm";
import MlTasksService from "services/MlTasksService";
import { ML_TASK_METRICS } from "urls";

const EditMlTaskMetricFormContainer = () => {
  const navigate = useNavigate();

  const { metricId } = useParams();

  const { useAlwaysGetGlobalMetric, useUpdateGlobalMetric } = MlTasksService();

  const { isLoading: isGetGlobalMetricLoading, metric } = useAlwaysGetGlobalMetric(metricId);

  const { onUpdate, isLoading: isUpdateGlobalMetricLoading } = useUpdateGlobalMetric(metricId);

  const redirect = () => navigate(ML_TASK_METRICS);

  const onSubmit = (formData) => {
    onUpdate(formData).then(() => {
      redirect();
    });
  };

  const onCancel = () => redirect();

  const defaultValues = useMemo(
    () => ({
      [ML_TASK_METRIC_FORM_FIELD_NAMES.NAME]: metric.name ?? "",
      [ML_TASK_METRIC_FORM_FIELD_NAMES.TENDENCY]: metric.tendency ?? "",
      [ML_TASK_METRIC_FORM_FIELD_NAMES.TARGET_VALUE]: metric.target_value ?? "",
      [ML_TASK_METRIC_FORM_FIELD_NAMES.FUNCTION]: metric.func ?? ""
    }),
    [metric.name, metric.func, metric.target_value, metric.tendency]
  );

  return (
    <MlTaskMetricForm
      defaultValues={defaultValues}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isGetLoading={isGetGlobalMetricLoading}
      isSubmitLoading={isUpdateGlobalMetricLoading}
      isEdit
    />
  );
};

export default EditMlTaskMetricFormContainer;
