import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import { Typography } from "@mui/material";
import Link from "@mui/material/Link";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import Circle from "components/Circle";
import CloudLabel from "components/CloudLabel";
import CloudType from "components/CloudType";
import FormattedMoney from "components/FormattedMoney";
import IconLabel from "components/IconLabel";
import Table from "components/Table";
import Expander from "components/Table/components/Expander";
import TableLoader from "components/TableLoader";
import Tooltip from "components/Tooltip";
import { intl } from "translations/react-intl-config";
import { CLOUD_ACCOUNT_CONNECT } from "urls";
import { getColorScale } from "utils/charts";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { BILLING_IMPORT_STATUS, getBillingImportStatus, summarizeChildrenDetails } from "utils/dataSources";
import useStyles from "./CloudAccountsTable.styles";

const NameCell = ({
  row: {
    original: {
      id,
      name,
      type,
      details: { cost } = {},
      last_import_at: lastImportAt,
      last_import_attempt_at: lastImportAttemptAt,
      last_import_attempt_error: lastImportAttemptError,
      children
    },
    index
  },
  colorScale
}) => {
  const importStatus = getBillingImportStatus({
    timestamp: lastImportAt,
    attemptTimestamp: lastImportAttemptAt,
    error: lastImportAttemptError
  });

  return (
    <CaptionedCell
      caption={
        importStatus === BILLING_IMPORT_STATUS.ERROR
          ? {
              key: "import_failed",
              node: (
                <Typography component="div" variant="caption">
                  <Tooltip title={lastImportAttemptError}>
                    <span>
                      <IconLabel
                        icon={<ErrorOutlineOutlinedIcon fontSize="inherit" color="error" />}
                        label={<FormattedMessage id="billingImportFailed" />}
                      />
                    </span>
                  </Tooltip>
                </Typography>
              )
            }
          : undefined
      }
    >
      <CloudLabel
        id={id}
        name={name}
        type={type}
        dataTestId={`link_cloud_${index}`}
        startAdornment={cost && !children ? <Circle color={colorScale(id)} mr={1} /> : null}
      />
    </CaptionedCell>
  );
};

const CloudAccountsTable = ({ cloudAccounts = [], isLoading = false }) => {
  const navigate = useNavigate();

  const theme = useTheme();

  const { classes } = useStyles();

  const columns = useMemo(() => {
    const colorScale = getColorScale(theme.palette.chart);
    return [
      {
        header: intl.formatMessage({ id: "name" }),
        accessorKey: "name",
        cell: (cellData) => (
          <div className={classes.nameCellWrapper}>
            <Expander row={cellData.row} />
            <NameCell {...cellData} colorScale={colorScale} />
          </div>
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
  }, [theme.palette.chart, classes.nameCellWrapper]);

  const data = useMemo(
    () =>
      cloudAccounts
        .map((dataSource) => {
          const { id } = dataSource;
          const children = cloudAccounts.filter(({ parent_id: parentId }) => parentId === id);
          const childrenDetails = summarizeChildrenDetails(children);
          return { ...dataSource, children, details: { ...dataSource.details, ...childrenDetails } };
        })
        .filter(({ parent_id: parentId }) => !parentId),
    [cloudAccounts]
  );

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
      pageSize={50}
      withExpanded
      actionBar={{
        show: true,
        definition: actionBarDefinition
      }}
    />
  );
};

export default CloudAccountsTable;
