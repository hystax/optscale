import { useEffect } from "react";
import { FormControl, FormLabel } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import SubTitle from "components/SubTitle";
import { DatasetNavigator, FormButtons, NameField, SelectedDatasets } from "./FormElements";

const LeaderboardDatasetForm = ({ defaultValues, onSubmit, onCancel, datasets, isLoadingProps = {} }) => {
  const { isGetDataLoading = false, isSubmitDataLoading = false } = isLoadingProps;

  const methods = useForm({
    defaultValues
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...defaultValues
    }));
  }, [defaultValues, reset]);

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate data-test-id="leaderboard_criteria_form">
        <NameField isLoading={isGetDataLoading} />
        <FormLabel>
          <FormattedMessage id="datasets" />
        </FormLabel>
        <FormControl fullWidth>
          <SubTitle>
            <FormattedMessage id="selectedDatasets" />
          </SubTitle>
          <SelectedDatasets isLoading={isGetDataLoading} />
        </FormControl>
        <FormControl fullWidth>
          <SubTitle>
            <FormattedMessage id="datasetNavigator" />
          </SubTitle>
          <DatasetNavigator datasets={datasets} isLoading={isGetDataLoading} />
        </FormControl>
        <FormButtons onCancel={onCancel} isLoading={isGetDataLoading || isSubmitDataLoading} />
      </form>
    </FormProvider>
  );
};

export default LeaderboardDatasetForm;
