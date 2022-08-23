import React, { useMemo } from "react";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TagKey from "components/TagKey";
import TextWithDataTestId from "components/TextWithDataTestId";
import TextWithDate from "components/TextWithDate";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const getTotalBreakdownTableData = (counts) =>
  Object.entries(counts).map(([id, { name = "", ...details }]) => ({
    id: id ?? name,
    name,
    ...details
  }));

const TagsBreakdownTable = ({ data, appliedRange, isLoading, selectedTag, onShowOnChartClick }) => {
  const tableData = useMemo(() => getTotalBreakdownTableData(data), [data]);

  const columns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_tag_key">
            <FormattedMessage id="tagKey" />
          </TextWithDataTestId>
        ),
        accessor: "tag",
        Cell: ({ cell: { value } }) => <TagKey tagKey={value} />
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_resource_count">
            <TextWithDate
              text={<FormattedMessage id="resourceCount" />}
              startDateTimestamp={appliedRange.startSecondsTimestamp}
              endDateTimestamp={appliedRange.endSecondsTimestamp}
            />
          </TextWithDataTestId>
        ),
        accessor: "count"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_expenses">
            <TextWithDate
              text={<FormattedMessage id="expenses" />}
              startDateTimestamp={appliedRange.startSecondsTimestamp}
              endDateTimestamp={appliedRange.endSecondsTimestamp}
            />
          </TextWithDataTestId>
        ),
        accessor: "cost",
        Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />,
        defaultSort: "desc"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        disableSortBy: true,
        Cell: ({ row: { original: { tag } = {}, index } }) => (
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
    [appliedRange.startSecondsTimestamp, appliedRange.endSecondsTimestamp, onShowOnChartClick, selectedTag]
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

TagsBreakdownTable.propTypes = {
  data: PropTypes.array.isRequired,
  appliedRange: PropTypes.object.isRequired,
  isLoading: PropTypes.bool,
  onShowOnChartClick: PropTypes.func,
  selectedTag: PropTypes.string
};

export default TagsBreakdownTable;
