import { useAwsDataSources } from "hooks/useAwsDataSources";
import { BucketsField, DataSourcesField, FormButtons, SizeField } from "./FormElements";
import { CreateS3DuplicateFinderCheckFormProps } from "./types";

const CreateS3DuplicateFinderCheckForm = ({
  buckets,
  onSubmit,
  onCancel,
  isLoadingProps = {}
}: CreateS3DuplicateFinderCheckFormProps) => {
  const { isSubmitLoading = false, isGetBucketsLoading = false } = isLoadingProps;

  const awsDataSources = useAwsDataSources();

  return (
    <form onSubmit={onSubmit} noValidate>
      <DataSourcesField dataSources={awsDataSources} />
      <BucketsField buckets={buckets} dataSources={awsDataSources} isLoading={isGetBucketsLoading} />
      <SizeField />
      <FormButtons onCancel={onCancel} isLoading={isSubmitLoading || isGetBucketsLoading} />
    </form>
  );
};

export default CreateS3DuplicateFinderCheckForm;
