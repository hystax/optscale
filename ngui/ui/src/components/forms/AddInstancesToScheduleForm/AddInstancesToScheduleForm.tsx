import { DataSourcesField, FiltersField, FormButtons, InstancesField } from "./FormElements";

const AddInstancesToScheduleForm = ({
  onSubmit,
  instances,
  onCancel,
  filterValues,
  instancesCountLimit,
  isLoadingProps = {}
}) => {
  const { isSubmitLoading = false, isGetInstancesLoading = false, isGetFilterValuesLoading = false } = isLoadingProps;

  return (
    <form onSubmit={onSubmit} noValidate>
      <DataSourcesField />
      <FiltersField filterValues={filterValues} isLoading={isGetFilterValuesLoading} />
      <InstancesField instances={instances} isLoading={isGetInstancesLoading} instancesCountLimit={instancesCountLimit} />
      <FormButtons onCancel={onCancel} isLoading={isSubmitLoading} />
    </form>
  );
};

export default AddInstancesToScheduleForm;
