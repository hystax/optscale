import { useMemo } from "react";
import { Box, Typography } from "@mui/material";
import { Stack } from "@mui/system";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import { SI_UNITS, useFormatDigitalUnit } from "components/FormattedDigitalUnit";
import { useMoneyFormatter } from "components/FormattedMoney";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import KeyValueLabel from "components/KeyValueLabel";
import SubTitle from "components/SubTitle";
import Table from "components/Table";
import DownloadObjectsListContainer from "containers/DownloadObjectsListContainer";
import { useAwsDataSources } from "hooks/useAwsDataSources";
import { text } from "utils/columns";
import dataSource from "utils/columns/dataSource";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const BucketsTable = ({ fromBucket, toBucket }) => {
  const awsDataSources = useAwsDataSources();

  const data = useMemo(() => {
    const getRowData = (bucket) => {
      const bucketDataSource = awsDataSources.find(({ id }) => id === bucket.cloud_account_id);

      return {
        ...bucket,
        cloud_account_id: bucketDataSource?.id,
        cloud_account_name: bucketDataSource?.name,
        cloud_account_type: bucketDataSource?.type
      };
    };

    const dataArray = [getRowData(fromBucket)];

    if (toBucket.name !== fromBucket.name) {
      dataArray.push(getRowData(toBucket));
    }

    return dataArray;
  }, [awsDataSources, fromBucket, toBucket]);

  const columns = useMemo(
    () => [
      text({
        headerDataTestId: "lbl_buckets",
        headerMessageId: "buckets",
        accessorKey: "name"
      }),
      dataSource()
    ],
    []
  );

  return <Table data={data} columns={columns} />;
};

const Duplicates = ({ crossBucketsStats }) => {
  const formatMoney = useMoneyFormatter();
  const formatDigitalUnit = useFormatDigitalUnit();

  return (
    <Box>
      <KeyValueLabel value={crossBucketsStats.duplicated_objects} messageId="duplicatedObjects" />
      <KeyValueLabel
        value={formatDigitalUnit({
          value: crossBucketsStats.duplicates_size,
          baseUnit: SI_UNITS.BYTE
        })}
        messageId="duplicatesSize"
      />
      <KeyValueLabel
        value={formatMoney(FORMATTED_MONEY_TYPES.COMMON, crossBucketsStats.monthly_savings)}
        messageId="possibleMonthlySavings"
      />
    </Box>
  );
};

const SelectedBucketsInfo = ({ onClose, fromBucket, toBucket, crossBucketsStats, checkId }) => (
  <>
    <Stack spacing={SPACING_2}>
      <div>
        <Typography>
          <FormattedMessage
            id="crossBucketDuplicatesApplySavings"
            values={{
              bucketName: <strong>{fromBucket.name}</strong>
            }}
          />
        </Typography>
      </div>
      <div>
        <BucketsTable fromBucket={fromBucket} toBucket={toBucket} />
      </div>
      <div>
        <SubTitle>
          <FormattedMessage id="duplicates" />
        </SubTitle>
        <Duplicates crossBucketsStats={crossBucketsStats} />
      </div>
    </Stack>
    <FormButtonsWrapper>
      <DownloadObjectsListContainer checkId={checkId} fromBucketName={fromBucket.name} toBucketName={toBucket.name} />
      <Button messageId="cancel" onClick={onClose} />
    </FormButtonsWrapper>
  </>
);

export default SelectedBucketsInfo;
