import { useEffect } from "react";
import { Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import CreateS3DuplicateFinderCheckForm, { FIELD_NAMES } from "components/CreateS3DuplicateFinderCheckForm";
import CloudResourcesService from "services/CloudResourcesService";
import S3DuplicatesService from "services/S3DuplicatesService";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { AWS_CNR } from "utils/constants";

const defaultValues = {
  [FIELD_NAMES.DATA_SOURCES_FIELD_NAME]: [],
  [FIELD_NAMES.BUCKETS_FIELD_NAME]: {},
  [FIELD_NAMES.SIZE_FIELD_NAME]: 0
};

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

  const methods = useForm({
    defaultValues
  });

  const { handleSubmit, watch } = methods;

  const selectedDataSources = watch(FIELD_NAMES.DATA_SOURCES_FIELD_NAME);

  const { buckets, isLoading: isGetBucketsLoading } = useGetBuckets(selectedDataSources);

  const onSubmit = (formData) => {
    const selectedBucketNames = Object.keys(formData[FIELD_NAMES.BUCKETS_FIELD_NAME]);
    const selectedBuckets = buckets.filter(({ name }) => selectedBucketNames.includes(name));

    onCreate({
      filters: {
        min_size: Number(formData[FIELD_NAMES.SIZE_FIELD_NAME]) * 1024 * 1024,
        buckets: selectedBuckets.map(({ name, cloud_account_id: cloudAccountId }) => ({
          name,
          cloud_account_id: cloudAccountId
        }))
      }
    }).then(handleClose);
  };

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
          onSubmit={handleSubmit(onSubmit)}
        />
      </FormProvider>
    </>
  );
};

export default CreateS3DuplicateFinderCheckContainer;
