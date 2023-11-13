import PlayCircleOutlineIcon from "@mui/icons-material/PlayCircleOutline";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useAwsDataSources } from "hooks/useAwsDataSources";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { BucketsField, DataSourcesField, SizeField } from "./FormElements";

const CreateS3DuplicateFinderCheckForm = ({ onSubmit, buckets, onCancel, isLoadingProps = {} }) => {
  const { isSubmitLoading = false, isGetBucketsLoading = false } = isLoadingProps;
  const { isDemo } = useOrganizationInfo();

  const awsDataSources = useAwsDataSources();

  return (
    <form onSubmit={onSubmit} noValidate>
      <DataSourcesField dataSources={awsDataSources} />
      <BucketsField buckets={buckets} dataSources={awsDataSources} isLoading={isGetBucketsLoading} />
      <SizeField />
      <FormButtonsWrapper mt={2} mb={2}>
        <ButtonLoader
          messageId="run"
          dataTestId="btn_run"
          color="primary"
          variant="contained"
          type="submit"
          startIcon={<PlayCircleOutlineIcon fontSize="small" />}
          isLoading={isSubmitLoading || isGetBucketsLoading}
          disabled={isDemo}
          tooltip={{
            show: isDemo,
            value: <FormattedMessage id="notAvailableInLiveDemo" />
          }}
        />
        <Button messageId="cancel" dataTestId="btn_cancel" onClick={onCancel} />
      </FormButtonsWrapper>
    </form>
  );
};

export default CreateS3DuplicateFinderCheckForm;
