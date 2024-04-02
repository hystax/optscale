import { useEffect, useMemo } from "react";
import RemoveOutlinedIcon from "@mui/icons-material/RemoveOutlined";
import { FormHelperText } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { datasetLabels, leaderboardCriteriaDataset } from "utils/columns";
import { EN_FULL_FORMAT, formatUTC } from "utils/datetime";
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
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_training_set">
            <FormattedMessage id="trainingSet" />
          </TextWithDataTestId>
        ),
        id: "trainingSet",
        accessorFn: (originalRow) => originalRow.training_set?.path,
        enableSorting: false,
        cell: ({
          cell,
          row: {
            original: {
              training_set: { timespan_from: timespanFrom, timespan_to: timespanTo }
            }
          }
        }) => (
          <CaptionedCell
            caption={[
              {
                key: "timespanFrom",
                node: (
                  <KeyValueLabel
                    keyMessageId="from"
                    value={timespanFrom ? formatUTC(timespanFrom, EN_FULL_FORMAT) : undefined}
                    variant="caption"
                  />
                )
              },
              {
                key: "timespanTo",
                node: (
                  <KeyValueLabel
                    keyMessageId="to"
                    value={timespanTo ? formatUTC(timespanTo, EN_FULL_FORMAT) : undefined}
                    variant="caption"
                  />
                )
              }
            ]}
          >
            {cell.getValue()}
          </CaptionedCell>
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_validation_set">
            <FormattedMessage id="validationSet" />
          </TextWithDataTestId>
        ),
        id: "validationSet",
        accessorFn: (originalRow) => originalRow.validation_set?.path,
        enableSorting: false,
        cell: ({
          cell,
          row: {
            original: {
              validation_set: { timespan_from: timespanFrom, timespan_to: timespanTo }
            }
          }
        }) => (
          <CaptionedCell
            caption={[
              {
                key: "timespanFrom",
                node: (
                  <KeyValueLabel
                    keyMessageId="from"
                    value={timespanFrom ? formatUTC(timespanFrom, EN_FULL_FORMAT) : undefined}
                    variant="caption"
                  />
                )
              },
              {
                key: "timespanTo",
                node: (
                  <KeyValueLabel
                    keyMessageId="to"
                    value={timespanTo ? formatUTC(timespanTo, EN_FULL_FORMAT) : undefined}
                    variant="caption"
                  />
                )
              }
            ]}
          >
            {cell.getValue()}
          </CaptionedCell>
        )
      }
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

const SelectedDatasets = ({ isLoading }) => {
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
          required: (value) => (isEmptyArray(value) ? intl.formatMessage({ id: "atLeastOneDatasetShouldBeSelected" }) : true)
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
