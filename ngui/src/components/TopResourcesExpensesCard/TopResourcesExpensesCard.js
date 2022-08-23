import React, { useMemo } from "react";
import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import FormattedMoney from "components/FormattedMoney";
import ResourceCell from "components/ResourceCell";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import WrapperCard from "components/WrapperCard";
import { getLast30DaysResourcesUrl } from "urls";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const TopResourcesExpensesCard = ({ cleanExpenses, isLoading }) => {
  const navigate = useNavigate();

  const goToResources = () => navigate(getLast30DaysResourcesUrl());

  const tableData = useMemo(
    () =>
      cleanExpenses.map((cleanExpense) => ({
        ...cleanExpense,
        resource: `${cleanExpense.cloud_resource_id} ${cleanExpense.resource_name}`
      })),
    [cleanExpenses]
  );

  const columns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="block_top_expenses_lbl_resource">
            <FormattedMessage id="resource" />
          </TextWithDataTestId>
        ),
        accessor: "resource",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        Cell: ({ row: { original, index } }) => (
          <ResourceCell
            disableActivityIcon
            disableConstraintViolationIcon
            rowData={original}
            dataTestIds={{ labelIds: { label: `block_top_expenses_link_resource_${index}` } }}
          />
        )
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="block_top_expenses_lbl_expenses">
            <FormattedMessage id="expenses" />
          </TextWithDataTestId>
        ),
        accessor: "cost",
        Cell: ({ row: { original } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.cost} />,
        defaultSort: "desc"
      }
    ],
    []
  );

  return (
    <WrapperCard
      needAlign
      title={<FormattedMessage id="topResourcesExpenses" />}
      titleCaption={<FormattedMessage id="lastValueDays" values={{ value: 30 }} />}
      titleButton={{
        type: "icon",
        tooltip: {
          title: <FormattedMessage id="goToResources" />
        },
        buttonProps: {
          icon: <ExitToAppOutlinedIcon />,
          isLoading,
          onClick: goToResources,
          dataTestId: "btn_go_to_resources"
        }
      }}
      dataTestIds={{
        wrapper: "block_top_resources",
        title: "lbl_top_resources",
        titleCaption: "p_last_30_days"
      }}
    >
      {isLoading ? (
        <TableLoader columnsCounter={columns.length} showHeader />
      ) : (
        <Table data={tableData} columns={columns} localization={{ emptyMessageId: "noResources" }} />
      )}
    </WrapperCard>
  );
};

TopResourcesExpensesCard.propTypes = {
  cleanExpenses: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default TopResourcesExpensesCard;
