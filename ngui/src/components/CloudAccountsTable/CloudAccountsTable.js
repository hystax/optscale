import React, { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import Link from "@mui/material/Link";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import Circle from "components/Circle";
import CloudLabel from "components/CloudLabel";
import CloudType from "components/CloudType";
import FormattedMoney from "components/FormattedMoney";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { intl } from "translations/react-intl-config";
import { CLOUD_ACCOUNT_CONNECT } from "urls";
import { getColorScale } from "utils/charts";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

const CloudAccountsTable = ({ cloudAccounts = [], isLoading = false }) => {
  const navigate = useNavigate();

  const theme = useTheme();

  const columns = useMemo(() => {
    const colorScale = getColorScale(theme.palette.chart);
    return [
      {
        header: intl.formatMessage({ id: "name" }),
        accessorKey: "name",
        cell: ({
          row: {
            original: { id, name, type, details: { cost } = {} },
            index
          }
        }) => (
          <CloudLabel
            id={id}
            name={name}
            type={type}
            dataTestId={`link_cloud_${index}`}
            startAdornment={cost ? <Circle color={colorScale(id)} mr={1} /> : null}
          />
        )
      },
      {
        header: intl.formatMessage({ id: "type" }),
        accessorKey: "type",
        cell: ({ cell }) => <CloudType type={cell.getValue()} />
      },
      {
        header: intl.formatMessage({ id: "resourcesChargedThisMonth" }),
        id: "details.tracked",
        accessorFn: (originalRow) => originalRow.details?.tracked,
        emptyValue: "0"
      },
      {
        header: intl.formatMessage({ id: "expensesUpToDateThisMonth" }),
        id: "details.cost",
        accessorFn: (originalRow) => originalRow.details?.cost,
        cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />,
        defaultSort: "desc"
      },
      {
        header: intl.formatMessage({ id: "expensesForecastThisMonth" }),
        id: "details.forecast",
        accessorFn: (originalRow) => originalRow.details?.forecast,
        cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
      }
    ];
  }, [theme.palette.chart]);

  const data = useMemo(() => cloudAccounts, [cloudAccounts]);

  const actionBarDefinition = {
    items: [
      {
        key: "bu-add",
        dataTestId: "btn_add",
        icon: <AddOutlinedIcon fontSize="small" />,
        messageId: "add",
        color: "success",
        variant: "contained",
        type: "button",
        action: () => navigate(CLOUD_ACCOUNT_CONNECT),
        requiredActions: ["MANAGE_CLOUD_CREDENTIALS"]
      }
    ]
  };

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Table
      dataTestIds={{
        container: "table_accs"
      }}
      data={data}
      columns={columns}
      localization={{
        emptyMessageId: "noDataSourcesWithLink",
        values: {
          connectCloudLink: (chunks) => (
            <Link to={CLOUD_ACCOUNT_CONNECT} component={RouterLink}>
              {chunks}
            </Link>
          )
        }
      }}
      actionBar={{
        show: true,
        definition: actionBarDefinition
      }}
    />
  );
};

CloudAccountsTable.propTypes = {
  cloudAccounts: PropTypes.array,
  isLoading: PropTypes.bool
};

export default CloudAccountsTable;
