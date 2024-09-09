import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MlMetricForm from "components/forms/MlMetricForm";
import { FIELD_NAMES } from "components/forms/MlMetricForm/constants";
import MlMetricsService from "services/MlMetricsService";
import { ML_METRICS } from "urls";

const EditMlMetricFormContainer = () => {
  const navigate = useNavigate();

  const { metricId } = useParams();

  const { useAlwaysGetMlMetric, useUpdateMlMetric } = MlMetricsService();

  const { isLoading: isGetGlobalMetricLoading, metric } = useAlwaysGetMlMetric(metricId);

  const { onUpdate, isLoading: isUpdateMlMetricLoading } = useUpdateMlMetric(metricId);

  const redirect = () => navigate(ML_METRICS);

  const onSubmit = (formData) => {
    onUpdate(formData).then(() => {
      redirect();
    });
  };

  const onCancel = () => redirect();

  const defaultValues = useMemo(
    () => ({
      [FIELD_NAMES.NAME]: metric.name ?? "",
      [FIELD_NAMES.TENDENCY]: metric.tendency ?? "",
      [FIELD_NAMES.TARGET_VALUE]: metric.target_value ?? "",
      [FIELD_NAMES.FUNCTION]: metric.func ?? ""
    }),
    [metric.name, metric.func, metric.target_value, metric.tendency]
  );

  return (
    <MlMetricForm
      defaultValues={defaultValues}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isGetLoading={isGetGlobalMetricLoading}
      isSubmitLoading={isUpdateMlMetricLoading}
      isEdit
    />
  );
};

export default EditMlMetricFormContainer;
