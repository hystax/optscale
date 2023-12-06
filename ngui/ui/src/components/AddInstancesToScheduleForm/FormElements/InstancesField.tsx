import { useMemo } from "react";
import { FormControl, FormHelperText, Stack } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import CollapsableTableCell from "components/CollapsableTableCell";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { powerScheduleInstance, resourceLocation, resourcePoolOwner, size } from "utils/columns";
import { SPACING_1 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";

export const FIELD_NAME = "instances";

const TableField = ({ instances, value, onChange }) => {
  const tableData = useMemo(() => instances, [instances]);

  const columns = useMemo(
    () => [
      powerScheduleInstance({
        idAccessor: "resource_id",
        nameAccessor: "resource_name",
        powerScheduleAccessor: "power_schedule",
        headerDataTestId: "lbl_instance_to_add",
        titleMessageId: "instance"
      }),
      resourcePoolOwner({
        id: "pool/owner",
        accessorFn: (rowOriginal) => {
          const { owner: { name: ownerName } = {} } = rowOriginal;
          const {
            pool: { name: poolName }
          } = rowOriginal;

          return [poolName, ownerName].filter((str) => str !== "").join(" ");
        },
        getOwner: (rowOriginal) => {
          const { owner } = rowOriginal;

          return owner
            ? {
                name: owner.name
              }
            : undefined;
        },
        getPool: (rowOriginal) => {
          const { pool } = rowOriginal;

          return pool
            ? {
                id: pool.id,
                name: pool.name,
                purpose: pool.purpose
              }
            : undefined;
        }
      }),
      resourceLocation({
        headerDataTestId: "lbl_location",
        typeAccessor: "cloud_account_type"
      }),
      size({
        id: "size",
        accessorFn: (originalRow) => originalRow.meta?.flavor,
        headerDataTestId: "lbl_size"
      }),
      {
        id: "tags",
        header: (
          <TextWithDataTestId dataTestId="lbl_tags">
            <FormattedMessage id="tags" />
          </TextWithDataTestId>
        ),
        cell: ({
          row: {
            original: { tags = {} }
          }
        }) => <CollapsableTableCell maxRows={5} tags={tags} />,
        accessorFn: (originalRow) =>
          Object.entries(originalRow.tags ?? {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" ")
      }
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
      queryParamPrefix="addInstancesToSchedule"
      localization={{
        emptyMessageId: "noInstances"
      }}
      counters={{ showCounters: true, hideTotal: false, hideDisplayed: true }}
    />
  );
};

const InstancesField = ({ instances, instancesCountLimit, isLoading = false }) => {
  const {
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <FormControl fullWidth>
      <Controller
        name={FIELD_NAME}
        rules={{
          validate: {
            atLeastOneSelected: (value) =>
              isEmptyObject(value) ? <FormattedMessage id="atLeastOneInstanceShouldBeSelected" /> : true
          }
        }}
        render={({ field: { value, onChange } }) => (
          <>
            {isLoading ? (
              <TableLoader />
            ) : (
              <Stack spacing={SPACING_1}>
                {instances.length >= instancesCountLimit && (
                  <div>
                    <InlineSeverityAlert
                      messageId="rowsLimitWarning"
                      messageValues={{
                        entities: intl.formatMessage({ id: "instances" }).toLocaleLowerCase(),
                        count: instancesCountLimit
                      }}
                    />
                  </div>
                )}
                <div>
                  <TableField instances={instances} value={value} onChange={onChange} />
                </div>
              </Stack>
            )}
            {!!errors[FIELD_NAME] && <FormHelperText error>{errors[FIELD_NAME].message}</FormHelperText>}
          </>
        )}
      />
    </FormControl>
  );
};

export default InstancesField;
