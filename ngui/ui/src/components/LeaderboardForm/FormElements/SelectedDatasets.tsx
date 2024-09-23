import { useEffect, useMemo } from "react";
import RemoveOutlinedIcon from "@mui/icons-material/RemoveOutlined";
import { FormHelperText } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import { datasetLabels, datasetTimespan, leaderboardDataset, localTime } from "utils/columns";
import { secondsToMilliseconds } from "utils/datetime";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const ControlledTable = ({ selectedDatasets, onDatasetRemove }) => {
  const tableData = useMemo(() => selectedDatasets, [selectedDatasets]);

  const columns = useMemo(
    () => [
      {
        header: null,
        enableSorting: false,
        id: "actions",
        cell: ({
          row: {
            original: { id }
          }
        }) => (
          <TableCellActions
            items={[
              {
                key: "remove",
                messageId: "remove",
                icon: <RemoveOutlinedIcon fontSize="small" />,
                action: () => onDatasetRemove(selectedDatasets.filter((selectedDataset) => selectedDataset.id !== id))
              }
            ]}
          />
        )
      },
      leaderboardDataset({
        nameAccessor: "name",
        pathAccessor: "path",
        deletedAccessor: "deleted"
      }),
      localTime({
        id: "created_at",
        accessorFn: (originalRow) => secondsToMilliseconds(originalRow.created_at),
        headerDataTestId: "lbl_updated_at",
        headerMessageId: "createdAt",
        defaultSort: "desc"
      }),
      datasetLabels({
        id: "labels",
        accessorFn: (originalRow) => originalRow.labels
      }),
      datasetTimespan()
    ],
    [onDatasetRemove, selectedDatasets]
  );

  return (
    <Table
      data={tableData}
      columns={columns}
      pageSize={5}
      localization={{
        emptyMessageId: "noDatasets"
      }}
      counters={{
        show: false
      }}
    />
  );
};

const SelectedDatasets = ({ isLoading = false }) => {
  const {
    control,
    formState: { errors, isSubmitted },
    watch,
    trigger
  } = useFormContext<FormValues>();

  const selectedDatasets = watch(FIELD_NAMES.SELECTED_DATASETS);

  useEffect(() => {
    if (isSubmitted) {
      trigger(FIELD_NAMES.SELECTED_DATASETS);
    }
  }, [isSubmitted, selectedDatasets, trigger]);

  return (
    <Controller
      name={FIELD_NAMES.SELECTED_DATASETS}
      control={control}
      render={({ field: { value, onChange } }) =>
        isLoading ? (
          <TableLoader />
        ) : (
          <>
            <ControlledTable selectedDatasets={value} onDatasetRemove={onChange} />
            {!!errors[FIELD_NAMES.SELECTED_DATASETS] && (
              <FormHelperText error>{errors[FIELD_NAMES.SELECTED_DATASETS]?.message}</FormHelperText>
            )}
          </>
        )
      }
    />
  );
};

export default SelectedDatasets;
