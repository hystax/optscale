import React, { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import Link from "@mui/material/Link";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import Circle from "components/Circle";
import CloudLabel from "components/CloudLabel";
import FormattedMoney from "components/FormattedMoney";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { intl } from "translations/react-intl-config";
import { CLOUD_ACCOUNT_CONNECT } from "urls";
import { getColorScale } from "utils/charts";
import { CLOUD_ACCOUNT_TYPE, FORMATTED_MONEY_TYPES } from "utils/constants";

const CloudAccountsTable = ({ cloudAccounts = [], isLoading = false }) => {
  const navigate = useNavigate();

  const theme = useTheme();

  const columns = useMemo(() => {
    const colorScale = getColorScale(theme.palette.chart);
    return [
      {
        Header: intl.formatMessage({ id: "name" }),
        accessor: "name",
        Cell: ({
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
        Header: intl.formatMessage({ id: "type" }),
        accessor: "type",
        Cell: ({ cell: { value } }) => intl.formatMessage({ id: CLOUD_ACCOUNT_TYPE[value] })
      },
      {
        Header: intl.formatMessage({ id: "resourcesChargedThisMonth" }),
        accessor: "details.tracked",
        emptyValue: "0"
      },
      {
        Header: intl.formatMessage({ id: "expensesUpToDateThisMonth" }),
        accessor: "details.cost",
        Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />,
        defaultSort: "desc"
      },
      {
        Header: intl.formatMessage({ id: "expensesForecastThisMonth" }),
        accessor: "details.forecast",
        Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />
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
