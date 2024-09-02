import { FormProvider, useForm } from "react-hook-form";
import ResourcesPerspectiveValuesDescription from "components/ResourcesPerspectiveValuesDescription";
import { FormButtons, NameAutocompleteField, PayloadField, PerspectiveOverrideWarning } from "./FormElements";
import { getDefaultValues } from "./utils";

const CreateResourcePerspectiveForm = ({
  onSubmit,
  breakdownBy,
  breakdownData,
  filters,
  perspectiveNames,
  isLoading = false,
  onCancel
}) => {
  const methods = useForm({
    defaultValues: getDefaultValues({
      filters: {
        filterValues: filters.getFilterValuesForAppliedFilters(),
        appliedFilters: filters.getAppliedFilters()
      },
      breakdownBy,
      breakdownData
    })
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form noValidate onSubmit={handleSubmit(onSubmit)}>
        <NameAutocompleteField perspectiveNames={perspectiveNames} />
        <ResourcesPerspectiveValuesDescription
          breakdownBy={breakdownBy}
          breakdownData={breakdownData}
          filters={filters.getAppliedValues()}
        />
        <PayloadField />
        <PerspectiveOverrideWarning perspectiveNames={perspectiveNames} />
        <FormButtons onCancel={onCancel} isLoading={isLoading} />
      </form>
    </FormProvider>
  );
};

export default CreateResourcePerspectiveForm;
