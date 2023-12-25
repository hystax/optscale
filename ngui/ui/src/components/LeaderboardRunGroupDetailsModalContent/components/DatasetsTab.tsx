import { useMemo } from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { Link, Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getMlModelRunUrl } from "urls";
import { formatRunFullName } from "utils/ml";

const DatasetsTable = ({ datasets }) => {
  const tableData = useMemo(() => datasets, [datasets]);
  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_dataset">
            <FormattedMessage id="dataset" />
          </TextWithDataTestId>
        ),
        id: "dataset",
        style: {
          width: "500px"
        },
        cell: ({
          row: {
            original: { name, path }
          }
        }) => (
          <>
            <Typography gutterBottom>{name}</Typography>
            <Typography>{path}</Typography>
          </>
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_status">
            <FormattedMessage id="status" />
          </TextWithDataTestId>
        ),
        id: "covered_by",
        enableSorting: false,
        cell: ({
          row: {
            original: { covered_by: coveredBy }
          }
        }) => {
          if (coveredBy) {
            const { application_id: taskId, id: runId, number: runNumber, name: runName } = coveredBy;

            return (
              <Box display="inline-flex" flexWrap="wrap" alignItems="center">
                <CheckCircleIcon fontSize="small" color="success" />
                <FormattedMessage id="coveredBy" />
                &nbsp;
                <Link to={getMlModelRunUrl(taskId, runId)} component={RouterLink}>
                  {formatRunFullName(runNumber, runName)}
                </Link>
              </Box>
            );
          }
          return (
            <Box display="inline-flex" flexWrap="wrap" alignItems="center">
              <CancelIcon fontSize="small" color="error" />
              <FormattedMessage id="notCovered" />
            </Box>
          );
        }
      }
    ],
    []
  );

  return <Table data={tableData} columns={columns} />;
};

const DatasetsTab = ({ datasets, isLoading }) => (isLoading ? <TableLoader /> : <DatasetsTable datasets={datasets} />);

export default DatasetsTab;
