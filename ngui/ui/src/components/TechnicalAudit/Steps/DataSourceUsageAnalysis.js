import React, { useMemo } from "react";
import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import Button from "components/Button";
import CloudLabel from "components/CloudLabel";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import QuestionMark from "components/QuestionMark";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { INTEGRATIONS, ENVIRONMENTS, CLOUD_ACCOUNT_CONNECT } from "urls";
import { isEmpty } from "utils/arrays";
import { SPACING_1 } from "utils/layouts";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const redirectToCreateCloudAccount = (navigate) => navigate(CLOUD_ACCOUNT_CONNECT);

const DataSourceUsageAnalysis = ({ isConfirmed, onConfirm, dataSources = [], isLoadingProps }) => {
  const navigate = useNavigate();

  const tableData = useMemo(() => dataSources, [dataSources]);

  const hasTableData = !isEmpty(tableData);

  const { isGetDataSourceLoading = false } = isLoadingProps;

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_tb_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        cell: ({
          row: {
            original: { id, name, type },
            index
          }
        }) => <CloudLabel id={id} name={name} type={type} dataTestId={`link_cloud_${index}`} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_tb_status">
            <FormattedMessage id="status" />
          </TextWithDataTestId>
        ),
        accessorKey: "last_import_at",
        cell: ({ cell }) =>
          cell.getValue() === 0 ? <FormattedMessage id="dataIsUnderProcessing" /> : <FormattedMessage id="ready" />
      }
    ],
    []
  );

  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12}>
        <Typography component="div">
          <FormattedMessage
            id="technicalAudit.dataSourceUsageAnalysisDescription"
            values={{
              // TODO: probably need to remove p from app.json and component from here
              p: (chunks) => <p>{chunks}</p>,
              itEnvironmentsLink: (chunks) => (
                <Link to={ENVIRONMENTS} component={RouterLink}>
                  {chunks}
                </Link>
              ),
              integrationsLink: (chunks) => (
                <Link to={INTEGRATIONS} component={RouterLink}>
                  {chunks}
                </Link>
              )
            }}
          />
        </Typography>
        {hasTableData && (
          <Typography>
            <FormattedMessage id="technicalAudit.dataSourceUsageAnalysisTableDescription" />
          </Typography>
        )}
      </Grid>
      {isGetDataSourceLoading ? (
        <TableLoader columnsCounter={columns.length} showHeader />
      ) : (
        hasTableData && (
          <Grid item xs={12} lg={8} xl={6}>
            <Table
              data={tableData}
              columns={columns}
              localization={{
                emptyMessageId: "noDataSources"
              }}
            />
          </Grid>
        )
      )}
      <Grid item xs={12}>
        {hasTableData ? (
          <Box display="flex" alignItems="center">
            <FormControlLabel
              control={<Checkbox data-test-id="checkbox_connect_data_sources" checked={isConfirmed} onChange={onConfirm} />}
              label={
                <Typography>
                  <FormattedMessage id="technicalAudit.dataSourcesConnectionConfirmation" />
                </Typography>
              }
            />
            <QuestionMark
              dataTestId="connect_data_sources_help"
              messageId="technicalAudit.dataSourcesConnectionConfirmationHint"
              fontSize="small"
            />
          </Box>
        ) : (
          <FormButtonsWrapper mt={0}>
            <Button
              variant="contained"
              color="success"
              onClick={() => redirectToCreateCloudAccount(navigate)}
              messageId="connectDataSource"
            />
          </FormButtonsWrapper>
        )}
      </Grid>
    </Grid>
  );
};

DataSourceUsageAnalysis.propTypes = {
  isConfirmed: PropTypes.bool.isRequired,
  onConfirm: PropTypes.func.isRequired,
  dataSources: PropTypes.array,
  isLoadingProps: PropTypes.shape({
    isGetTechnicalAuditLoading: PropTypes.bool,
    isUpdateTechnicalAuditLoading: PropTypes.bool,
    isGetDataSourceLoading: PropTypes.bool
  })
};

export default DataSourceUsageAnalysis;
