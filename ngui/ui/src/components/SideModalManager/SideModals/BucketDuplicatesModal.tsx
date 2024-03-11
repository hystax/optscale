import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import CloudLabel from "components/CloudLabel";
import { SI_UNITS, formatDigitalUnit } from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import QuestionMark from "components/QuestionMark";
import { useAwsDataSources } from "hooks/useAwsDataSources";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseSideModal from "./BaseSideModal";

const Component = ({ bucket, onClose }) => {
  const awsDataSources = useAwsDataSources();
  const bucketDataSource = awsDataSources.find(({ id }) => id === bucket.cloud_account_id);

  return (
    <>
      <KeyValueLabel value={bucket.name} keyMessageId="bucket" />
      <KeyValueLabel
        value={
          bucketDataSource ? (
            <CloudLabel type={bucketDataSource.type} id={bucketDataSource.id} name={bucketDataSource.name} />
          ) : undefined
        }
        keyMessageId="dataSource"
      />
      <Box display="flex" alignItems="center">
        <KeyValueLabel
          value={
            <FormattedMessage
              id="value / value"
              values={{
                value1: bucket.objects_with_duplicates,
                value2: bucket.total_objects
              }}
            />
          }
          keyMessageId="totalObjectsWithDuplicates"
        />
        <QuestionMark
          messageId="totalObjectsWithDuplicatesDescription"
          messageValues={{
            i: (chunks) => <i>{chunks}</i>
          }}
          dataTestId="qmark_total_objects_with_duplicates_description`"
        />
      </Box>
      <Box display="flex" alignItems="center">
        <KeyValueLabel
          value={
            <>
              <FormattedMessage
                id="value / value"
                values={{
                  value1: formatDigitalUnit({
                    value: bucket.objects_with_duplicates_size,
                    baseUnit: SI_UNITS.BYTE
                  }),
                  value2: formatDigitalUnit({
                    value: bucket.size,
                    baseUnit: SI_UNITS.BYTE
                  })
                }}
              />
            </>
          }
          keyMessageId="totalDuplicatesSize"
        />
        <QuestionMark
          messageId="totalDuplicatesSizeDescription"
          messageValues={{
            i: (chunks) => <i>{chunks}</i>
          }}
          dataTestId="qmark_total_duplicates_size_description"
        />
      </Box>
      <KeyValueLabel
        value={<FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={bucket.monthly_savings} />}
        keyMessageId="possibleMonthlySavings"
      />
      <FormButtonsWrapper>
        <Button messageId="close" onClick={onClose} />
      </FormButtonsWrapper>
    </>
  );
};

class BucketDuplicatesModal extends BaseSideModal {
  headerProps = {
    messageId: "bucketDuplicatesTitle",
    dataTestIds: {
      title: "lbl_bucket_duplicates",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_bucket_duplicates";

  get content() {
    return <Component onClose={this.closeSideModal} bucket={this.payload?.bucket} />;
  }
}

export default BucketDuplicatesModal;
