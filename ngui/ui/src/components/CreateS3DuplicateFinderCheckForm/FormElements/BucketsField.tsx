import { useEffect, useMemo } from "react";
import { FormControl, FormHelperText } from "@mui/material";
import Typography from "@mui/material/Typography";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import CloudResourceId from "components/CloudResourceId";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { resourceLocation } from "utils/columns";
import { isEmpty as isEmptyObject } from "utils/objects";
import { getCloudResourceIdentifier } from "utils/resources";

export const FIELD_NAME = "buckets";

const MAX_SELECTED_BUCKETS = 100;

const TableField = ({ buckets, value, dataSources, onChange, errors }) => {
  const tableData = useMemo(
    () =>
      buckets.map((bucket) => {
        const dataSource = dataSources.find(({ id }) => id === bucket.cloud_account_id);
        return {
          ...bucket,
          cloud_account_type: dataSource?.type
        };
      }),
    [buckets, dataSources]
  );
  const columns = useMemo(
    () => [
      {
        id: "bucket",
        header: <FormattedMessage id="resourceType.bucket" />,
        accessorFn: (data) => getCloudResourceIdentifier(data),
        defaultSort: "asc",
        cell: ({ row: { original: bucket } }) => (
          <CloudResourceId
            disableLink
            cloudResourceIdentifier={getCloudResourceIdentifier({
              cloud_resource_id: bucket.cloud_resource_id,
              cloud_resource_hash: bucket.cloud_resource_hash
            })}
          />
        )
      },
      resourceLocation({
        headerDataTestId: "lbl_region",
        typeAccessor: "cloud_account_type"
      })
    ],
    []
  );

  return (
    <>
      <Table
        columns={columns}
        withSearch
        enableSearchQueryParam={false}
        data={tableData}
        memoBodyCells
        withSelection
        rowSelection={value}
        getRowId={(row) => getCloudResourceIdentifier(row)}
        onRowSelectionChange={onChange}
        pageSize={10}
        enablePaginationQueryParam={false}
        localization={{
          emptyMessageId: "noBuckets"
        }}
        counters={{ showCounters: true, hideTotal: false, hideDisplayed: true }}
      />
      {!!errors[FIELD_NAME] && <FormHelperText error>{errors[FIELD_NAME].message}</FormHelperText>}
    </>
  );
};

const BucketsField = ({ buckets, dataSources, isLoading }) => {
  const {
    formState: { errors },
    watch,
    trigger
  } = useFormContext();

  const selectedBuckets = watch(FIELD_NAME);

  useEffect(() => {
    /**
     * Trigger validation if some row is selected to be able to show "max-buckets" error before form was submitted
     */
    if (!isEmptyObject(selectedBuckets)) {
      trigger(FIELD_NAME);
    }
  }, [selectedBuckets, trigger]);

  return (
    <FormControl fullWidth>
      <Controller
        name={FIELD_NAME}
        rules={{
          validate: {
            atLeastOneSelected: (value) =>
              isEmptyObject(value) ? <FormattedMessage id="atLeastOneBucketShouldBeSelected" /> : true,
            maxBuckets: (value) => {
              const bucketsCount = Object.keys(value).length;
              return bucketsCount > MAX_SELECTED_BUCKETS ? (
                <FormattedMessage
                  id="maxNBucketsCanBeSelected"
                  values={{
                    value: MAX_SELECTED_BUCKETS
                  }}
                />
              ) : (
                true
              );
            }
          }
        }}
        render={({ field: { value, onChange } }) =>
          isLoading ? (
            <TableLoader />
          ) : (
            <>
              <TableField buckets={buckets} dataSources={dataSources} value={value} onChange={onChange} errors={errors} />
              {!isEmptyObject(selectedBuckets) && (
                // Intentionally avoided using KeyValue label due to inconvenience
                <Typography variant="caption">
                  <FormattedMessage id="selectedBuckets" />
                  &#58;&nbsp;
                  <strong>{Object.keys(selectedBuckets).join(", ")}</strong>
                </Typography>
              )}
            </>
          )
        }
      />
    </FormControl>
  );
};

export default BucketsField;
