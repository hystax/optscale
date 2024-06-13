import { useEffect } from "react";
import { Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import CreateS3DuplicateFinderCheckForm from "components/forms/CreateS3DuplicateFinderCheckForm";
import { FIELD_NAMES } from "components/forms/CreateS3DuplicateFinderCheckForm/constants";
import { FormValues } from "components/forms/CreateS3DuplicateFinderCheckForm/types";
import { getDefaultValues } from "components/forms/CreateS3DuplicateFinderCheckForm/utils";
import CloudResourcesService from "services/CloudResourcesService";
import S3DuplicatesService from "services/S3DuplicatesService";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { AWS_CNR } from "utils/constants";

const useGetBuckets = (dataSourceIds) => {
  const { useGetOnDemandOrganizationCloudResources } = CloudResourcesService();

  const { getData, isLoading, resources: buckets = [] } = useGetOnDemandOrganizationCloudResources();

  useEffect(() => {
    if (!isEmptyArray(dataSourceIds)) {
      getData({
        type: "bucket",
        cloud_type: AWS_CNR,
        filters: JSON.stringify({
          cloud_account_id: dataSourceIds
        })
      });
    }
  }, [getData, dataSourceIds]);

  return {
    buckets,
    isLoading
  };
};

const CreateS3DuplicateFinderCheckContainer = ({ handleClose }) => {
  const { useCreate } = S3DuplicatesService();
  const { onCreate, isLoading: isCreateLoading } = useCreate();

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues()
  });

  const { handleSubmit, watch } = methods;

  const selectedDataSources = watch(FIELD_NAMES.DATA_SOURCES);

  const { buckets, isLoading: isGetBucketsLoading } = useGetBuckets(selectedDataSources);

  const onSubmit = handleSubmit((formData) => {
    const selectedBucketNames = Object.keys(formData.buckets);
    const selectedBuckets = buckets.filter(({ name }) => selectedBucketNames.includes(name));

    onCreate({
      filters: {
        min_size: Number(formData.size) * 1024 * 1024,
        buckets: selectedBuckets.map(({ name, cloud_account_id: cloudAccountId }) => ({
          name,
          cloud_account_id: cloudAccountId
        }))
      }
    }).then(handleClose);
  });

  return (
    <>
      <Typography gutterBottom>
        <FormattedMessage id="createS3DuplicatesCheckDescription" />
      </Typography>
      <FormProvider {...methods}>
        <CreateS3DuplicateFinderCheckForm
          buckets={isEmptyArray(selectedDataSources) ? [] : buckets}
          onCancel={handleClose}
          isLoadingProps={{
            isSubmitLoading: isCreateLoading,
            isGetBucketsLoading
          }}
          onSubmit={onSubmit}
        />
      </FormProvider>
    </>
  );
};

export default CreateS3DuplicateFinderCheckContainer;
