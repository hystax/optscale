import { FormProvider, useForm } from "react-hook-form";
import { FILTER_TYPE } from "components/FilterComponents/constants";
import { FILTER_CONFIGS } from "components/Resources/filterConfigs";
import ResourcesPerspectiveValuesDescription from "components/ResourcesPerspectiveValuesDescription";
import { FormButtons, NameAutocompleteField, PayloadField, PerspectiveOverrideWarning } from "./FormElements";
import { getDefaultValues } from "./utils";

const CreateResourcePerspectiveForm = ({
  onSubmit,
  breakdownBy,
  breakdownData,
  perspectiveNames,
  isLoading = false,
  onCancel,
  filterValues,
  appliedFilters,
}) => {
  const perspectiveAppliedFilters = Object.values(FILTER_CONFIGS).reduce((acc, filterConfig) => {
    const key = filterConfig.id;

    return {
      ...acc,
      ...filterConfig.transformers.toApi(appliedFilters[key]),
    };
  }, {});

  const perspectiveFilterValues = Object.values(FILTER_CONFIGS).reduce((acc, filterConfig) => {
    const key = filterConfig.id;

    if (filterConfig.type === FILTER_TYPE.RANGE) {
      return acc;
    }

    if (filterConfig.type === FILTER_TYPE.SELECTION) {
      return {
        ...acc,
        [filterConfig.apiName]: filterConfig.transformers.filterFilterValuesByAppliedFilters(
          filterValues[filterConfig.apiName] ?? [],
          appliedFilters[key].values
        ),
      };
    }

    return acc;
  }, {});

  const methods = useForm({
    defaultValues: getDefaultValues({
      filters: {
        filterValues: perspectiveFilterValues,
        appliedFilters: perspectiveAppliedFilters,
      },
      breakdownBy,
      breakdownData,
    }),
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form noValidate onSubmit={handleSubmit(onSubmit)}>
        <NameAutocompleteField perspectiveNames={perspectiveNames} />
        <ResourcesPerspectiveValuesDescription
          breakdownBy={breakdownBy}
          breakdownData={breakdownData}
          perspectiveFilterValues={perspectiveFilterValues}
          perspectiveAppliedFilters={perspectiveAppliedFilters}
        />
        <PayloadField />
        <PerspectiveOverrideWarning perspectiveNames={perspectiveNames} />
        <FormButtons onCancel={onCancel} isLoading={isLoading} />
      </form>
    </FormProvider>
  );
};

export default CreateResourcePerspectiveForm;
