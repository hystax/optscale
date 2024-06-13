import { useEffect, useMemo } from "react";
import RemoveOutlinedIcon from "@mui/icons-material/RemoveOutlined";
import { FormHelperText } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { datasetLabels, datasetTimespan, leaderboardCriteriaDataset } from "utils/columns";
import { FIELD_NAMES } from "../constants";

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
      leaderboardCriteriaDataset({
        nameAccessor: "name",
        pathAccessor: "path",
        deletedAccessor: "deleted"
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
    />
  );
};

const SelectedDatasets = ({ isLoading = false }) => {
  const {
    control,
    formState: { errors, isSubmitted },
    watch,
    trigger
  } = useFormContext();
  const intl = useIntl();

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
      rules={{
        validate: {
          required: (value) => (isEmptyArray(value) ? intl.formatMessage({ id: "atLeastOneDatasetMustBeSelected" }) : true)
        }
      }}
      render={({ field: { value, onChange } }) =>
        isLoading ? (
          <TableLoader />
        ) : (
          <>
            <ControlledTable selectedDatasets={value} onDatasetRemove={onChange} />
            {!!errors[FIELD_NAMES.SELECTED_DATASETS] && (
              <FormHelperText error>{errors[FIELD_NAMES.SELECTED_DATASETS].message}</FormHelperText>
            )}
          </>
        )
      }
    />
  );
};

export default SelectedDatasets;
