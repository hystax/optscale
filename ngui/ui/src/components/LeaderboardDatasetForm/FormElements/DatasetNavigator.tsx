import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmpty } from "utils/arrays";
import { leaderboardCriteriaDataset, leaderboardCriteriaDatasetLabels } from "utils/columns";
import { EN_FULL_FORMAT, formatUTC } from "utils/datetime";
import { FIELD_NAMES } from "../constants";

const DatasetNavigator = ({ datasets, isLoading = false }) => {
  const intl = useIntl();

  const { setValue, watch } = useFormContext();
  const selectedDatasets = watch(FIELD_NAMES.SELECTED_DATASETS);

  const getRangeFilterDefinition = () => {
    const fromTimeSpans = datasets
      .flatMap(({ training_set: trainingSet, validation_set: validationSet }) => [
        trainingSet?.timespan_from,
        validationSet?.timespan_from
      ])
      .filter(Boolean);

    const toTimeSpans = datasets
      .flatMap(({ training_set: trainingSet, validation_set: validationSet }) => [
        trainingSet?.timespan_to,
        validationSet?.timespan_to
      ])
      .filter(Boolean);

    if (isEmpty(fromTimeSpans) || isEmpty(toTimeSpans)) {
      return undefined;
    }

    const minTimespan = Math.min(...fromTimeSpans);
    const maxTimespan = Math.max(...toTimeSpans);

    return {
      min: minTimespan,
      max: maxTimespan,
      step: 1,
      filterFn: (originalRow, range) => {
        const { training_set: trainingSet, validation_set: validationSet } = originalRow;

        const { timespan_from: trainingSetTimespanFrom, timespan_to: trainingSetTimespanTo } = trainingSet ?? {};
        const { timespan_from: validationSetTimespanFrom, timespan_to: validationSetTimespanTo } = validationSet ?? {};

        if (trainingSetTimespanFrom && trainingSetTimespanTo && validationSetTimespanFrom && validationSetTimespanTo) {
          return (
            (range[1] >= trainingSetTimespanFrom && trainingSetTimespanTo >= range[0]) ||
            (range[1] >= validationSetTimespanFrom && validationSetTimespanTo >= range[0])
          );
        }

        return true;
      },
      title: (range) =>
        intl.formatMessage(
          { id: "timerange" },
          { from: formatUTC(range[0], EN_FULL_FORMAT), to: formatUTC(range[1], EN_FULL_FORMAT) }
        )
    };
  };

  const tableData = useMemo(() => {
    const selectedDatasetIds = selectedDatasets.map(({ id }) => id);

    return datasets.filter(({ id }) => !selectedDatasetIds.includes(id)).map((dataset) => dataset);
  }, [datasets, selectedDatasets]);

  const columns = useMemo(
    () => [
      {
        header: null,
        enableSorting: false,
        id: "actions",
        cell: ({ row: { original } }) => (
          <TableCellActions
            items={[
              {
                key: "add",
                messageId: "add",
                icon: <AddOutlinedIcon fontSize="small" />,
                action: () => {
                  setValue(FIELD_NAMES.SELECTED_DATASETS, [...selectedDatasets, original]);
                }
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
      leaderboardCriteriaDatasetLabels(),
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
                    variant="caption"
                    value={timespanFrom ? formatUTC(timespanFrom, EN_FULL_FORMAT) : undefined}
                  />
                )
              },
              {
                key: "timespanTo",
                node: (
                  <KeyValueLabel
                    keyMessageId="to"
                    variant="caption"
                    value={timespanTo ? formatUTC(timespanTo, EN_FULL_FORMAT) : undefined}
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
        enableSorting: false,
        accessorFn: (originalRow) => originalRow.validation_set?.path,
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
                    variant="caption"
                    value={timespanFrom ? formatUTC(timespanFrom, EN_FULL_FORMAT) : undefined}
                  />
                )
              },
              {
                key: "timespanTo",
                node: (
                  <KeyValueLabel
                    keyMessageId="to"
                    variant="caption"
                    value={timespanTo ? formatUTC(timespanTo, EN_FULL_FORMAT) : undefined}
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
    [selectedDatasets, setValue]
  );

  return isLoading ? (
    <TableLoader />
  ) : (
    <Table
      data={tableData}
      columns={columns}
      withSearch
      pageSize={5}
      enableSearchQueryParam={false}
      enablePaginationQueryParam={false}
      localization={{
        emptyMessageId: "noDatasets"
      }}
      rangeFilter={getRangeFilterDefinition()}
    />
  );
};

export default DatasetNavigator;
