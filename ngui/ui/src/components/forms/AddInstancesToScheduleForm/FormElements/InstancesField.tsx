import { useMemo } from "react";
import { FormControl, FormHelperText } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import FormContentDescription from "components/FormContentDescription";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { powerScheduleInstance, resourceLocation, resourcePoolOwner, size, tags } from "utils/columns";
import { isEmptyObject } from "utils/objects";
import { FormValues } from "../types";

export const FIELD_NAME = "instances";

const TableField = ({ instances, value, onChange }) => {
  const tableData = useMemo(() => instances, [instances]);

  const columns = useMemo(
    () => [
      powerScheduleInstance({
        idAccessor: "resource_id",
        nameAccessor: "resource_name",
        activeAccessor: "active",
        powerScheduleAccessor: "power_schedule",
        headerDataTestId: "lbl_instance_to_add",
        titleMessageId: "instance",
      }),
      resourcePoolOwner({
        id: "pool/owner",
        accessorFn: (rowOriginal) => {
          const { owner: { name: ownerName } = {} } = rowOriginal;
          const {
            pool: { name: poolName },
          } = rowOriginal;

          return [poolName, ownerName].filter((str) => str !== "").join(" ");
        },
        getOwner: (rowOriginal) => {
          const { owner } = rowOriginal;

          return owner
            ? {
                name: owner.name,
              }
            : undefined;
        },
        getPool: (rowOriginal) => {
          const { pool } = rowOriginal;

          return pool
            ? {
                id: pool.id,
                name: pool.name,
                purpose: pool.purpose,
              }
            : undefined;
        },
      }),
      resourceLocation({
        headerDataTestId: "lbl_location",
        typeAccessor: "cloud_account_type",
      }),
      size({
        id: "size",
        accessorFn: (originalRow) => originalRow.meta?.flavor,
        headerDataTestId: "lbl_size",
      }),
      tags({
        id: "tags",
        accessorFn: (originalRow) =>
          Object.entries(originalRow.tags ?? {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" "),
        getTags: (originalRow) => originalRow.tags,
      }),
    ],
    []
  );

  return (
    <Table
      columns={columns}
      data={tableData}
      withSelection
      withSearch
      rowSelection={value}
      getRowId={(row) => row.id}
      onRowSelectionChange={onChange}
      pageSize={10}
      localization={{
        emptyMessageId: "noInstances",
      }}
      enableSearchQueryParam={false}
      enablePaginationQueryParam={false}
    />
  );
};

const InstancesField = ({ instances, instancesCountLimit, isLoading = false }) => {
  const {
    formState: { errors },
  } = useFormContext<FormValues>();

  const intl = useIntl();

  return (
    <Controller
      name={FIELD_NAME}
      rules={{
        validate: {
          atLeastOneSelected: (value) =>
            isEmptyObject(value) ? intl.formatMessage({ id: "atLeastOneInstanceMustBeSelected" }) : true,
        },
      }}
      render={({ field: { value, onChange } }) => {
        if (isLoading) {
          return (
            <FormControl fullWidth>
              <TableLoader />
            </FormControl>
          );
        }

        return (
          <>
            {instances.length >= instancesCountLimit && (
              <FormContentDescription
                alertProps={{
                  messageId: "rowsLimitWarning",
                  messageValues: {
                    entities: intl.formatMessage({ id: "instances" }).toLocaleLowerCase(),
                    count: instancesCountLimit,
                  },
                }}
              />
            )}
            <FormControl fullWidth>
              <TableField instances={instances} value={value} onChange={onChange} />
              {!!errors[FIELD_NAME] && <FormHelperText error>{errors[FIELD_NAME].message}</FormHelperText>}
            </FormControl>
          </>
        );
      }}
    />
  );
};

export default InstancesField;
