import SaveMlChartsDashboardForm from "components/forms/SaveMlChartsDashboardForm";
import LayoutsService from "services/LayoutsService";

const SaveMlChartsDashboardFormContainer = ({
  dashboard,
  isOwnedDashboard,
  updateDashboard,
  createDashboard,
  onSuccess,
  onCancel
}) => {
  const { useUpdate, useCreate } = LayoutsService();
  const { isLoading: isCreateLoading } = useCreate();
  const { isLoading: isUpdateLoading } = useUpdate();

  return (
    <SaveMlChartsDashboardForm
      dashboard={dashboard}
      isOwnedDashboard={isOwnedDashboard}
      updateDashboard={updateDashboard}
      createDashboard={createDashboard}
      onSuccess={onSuccess}
      onCancel={onCancel}
      isLoadingProps={{
        isSubmitLoading: isCreateLoading || isUpdateLoading
      }}
    />
  );
};

export default SaveMlChartsDashboardFormContainer;
