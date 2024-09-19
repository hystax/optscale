import { useMemo } from "react";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import { FormattedMessage, useIntl } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import TextWithDate from "components/TextWithDate";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const TagsBreakdownTable = ({ data, appliedRange, isLoading, selectedTag, onShowOnChartClick }) => {
  const tableData = useMemo(() => data, [data]);

  const intl = useIntl();

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_tag_key">
            <FormattedMessage id="tagKey" />
          </TextWithDataTestId>
        ),
        id: "tagKey",
        accessorFn: ({ tag }) =>
          tag ??
          intl.formatMessage({
            id: "(untagged)"
          })
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_resource_count">
            <TextWithDate
              text={<FormattedMessage id="resourceCount" />}
              startDateTimestamp={appliedRange.startSecondsTimestamp}
              endDateTimestamp={appliedRange.endSecondsTimestamp}
            />
          </TextWithDataTestId>
        ),
        accessorKey: "count"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_expenses">
            <TextWithDate
              text={<FormattedMessage id="expenses" />}
              startDateTimestamp={appliedRange.startSecondsTimestamp}
              endDateTimestamp={appliedRange.endSecondsTimestamp}
            />
          </TextWithDataTestId>
        ),
        accessorKey: "cost",
        cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />,
        defaultSort: "desc"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        enableSorting: false,
        cell: ({ row: { original: { tag } = {}, index } }) => (
          <TableCellActions
            items={[
              {
                key: "toggle",
                messageId: tag === selectedTag ? "showAllResources" : "showOnChart",
                icon: <BarChartOutlinedIcon />,
                dataTestId: `btn_toggle_${index}`,
                color: tag === selectedTag ? "secondary" : "primary",
                action: () => onShowOnChartClick(tag)
              }
            ]}
          />
        )
      }
    ],
    [appliedRange.startSecondsTimestamp, appliedRange.endSecondsTimestamp, intl, selectedTag, onShowOnChartClick]
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Table
      withSearch
      data={tableData}
      columns={columns}
      localization={{ emptyMessageId: "noTags" }}
      dataTestIds={{
        container: "tags_table"
      }}
      queryParamPrefix="tags"
      pageSize={50}
    />
  );
};

export default TagsBreakdownTable;
