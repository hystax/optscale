import { useEffect, useMemo } from "react";
import { FormControl, FormHelperText } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import CloudResourceId from "components/CloudResourceId";
import S3DuplicatesBucketsList from "components/S3DuplicatesBucketsList";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { resourceLocation } from "utils/columns";
import { isEmptyObject } from "utils/objects";
import { getCloudResourceIdentifier } from "utils/resources";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const FIELD_NAME = FIELD_NAMES.BUCKETS;

const MAX_SELECTED_BUCKETS = 100;

const VALIDATION_TYPE = {
  AT_LEAST_ONE_SELECTED: "atLeastOneSelected",
  MAX_BUCKETS: "maxBuckets",
} as const;

const TableField = ({ buckets, value, dataSources, onChange }) => {
  const tableData = useMemo(
    () =>
      buckets.map((bucket) => {
        const dataSource = dataSources.find(({ id }) => id === bucket.cloud_account_id);
        return {
          ...bucket,
          cloud_account_type: dataSource?.type,
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
              cloud_resource_hash: bucket.cloud_resource_hash,
            })}
          />
        ),
      },
      resourceLocation({
        headerDataTestId: "lbl_region",
        typeAccessor: "cloud_account_type",
      }),
    ],
    []
  );

  return (
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
        emptyMessageId: "noBuckets",
      }}
    />
  );
};

const BucketsField = ({ buckets, dataSources, isLoading }) => {
  const intl = useIntl();

  const {
    formState: { errors },
    watch,
    trigger,
  } = useFormContext<FormValues>();

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
            [VALIDATION_TYPE.AT_LEAST_ONE_SELECTED]: (value) =>
              isEmptyObject(value)
                ? intl.formatMessage({
                    id: "atLeastOneBucketMustBeSelected",
                  })
                : true,
            [VALIDATION_TYPE.MAX_BUCKETS]: (value) => {
              const bucketsCount = Object.keys(value).length;
              return bucketsCount > MAX_SELECTED_BUCKETS
                ? intl.formatMessage(
                    {
                      id: "maxNBucketsCanBeSelected",
                    },
                    {
                      value: MAX_SELECTED_BUCKETS,
                    }
                  )
                : true;
            },
          },
        }}
        render={({ field: { value, onChange } }) =>
          isLoading ? (
            <TableLoader />
          ) : (
            <>
              <TableField buckets={buckets} dataSources={dataSources} value={value} onChange={onChange} errors={errors} />
              {!isEmptyObject(selectedBuckets) && <S3DuplicatesBucketsList bucketNames={Object.keys(selectedBuckets)} />}
              {!!errors[FIELD_NAME] && <FormHelperText error>{errors[FIELD_NAME].message}</FormHelperText>}
            </>
          )
        }
      />
    </FormControl>
  );
};

export default BucketsField;
