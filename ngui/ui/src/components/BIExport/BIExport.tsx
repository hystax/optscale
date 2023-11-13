import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { Link } from "@mui/material";
import { Box } from "@mui/system";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import { BI_EXPORTS, INTEGRATIONS, getEditBIExportUrl } from "urls";
import { getBIExportActivityStatus, getBIExportStatus } from "utils/biExport";
import { FilesSummaryList, TargetStorageSummaryList } from "./Components";
import DetailsSummaryList from "./Components/DetailsSummaryList";

const BIExport = ({ biExport, isLoading = false }) => {
  const {
    id,
    name,
    type,
    days,
    created_at: createdAt = 0,
    last_run: lastRun = 0,
    last_completed: lastCompleted = 0,
    next_run: nextRun = 0,
    last_status_error: lastStatusError,
    meta,
    files = []
  } = biExport;

  const status = getBIExportStatus(biExport);

  const activity = getBIExportActivityStatus(biExport.status);

  return (
    <>
      <ActionBar
        data={{
          breadcrumbs: [
            <Link key={1} to={INTEGRATIONS} component={RouterLink}>
              <FormattedMessage id="integrations" />
            </Link>,
            <Link key={2} to={BI_EXPORTS} component={RouterLink}>
              <FormattedMessage id="biExportTitle" />
            </Link>
          ],
          title: {
            text: name,
            dataTestId: "lbl_bi_export",
            isLoading
          },
          items: [
            {
              key: "edit",
              icon: <EditOutlinedIcon />,
              messageId: "edit",
              type: "button",
              link: getEditBIExportUrl(id),
              isLoading,
              requiredActions: ["EDIT_PARTNER"]
            }
          ]
        }}
      />
      <PageContentWrapper>
        <Box display="flex" flexWrap="wrap" rowGap={1} columnGap={16}>
          <Box minWidth="250px">
            <DetailsSummaryList
              id={id}
              name={name}
              days={days}
              createdAt={createdAt}
              lastRun={lastRun}
              lastCompleted={lastCompleted}
              activity={activity}
              status={status}
              nextRun={nextRun}
              lastStatusError={lastStatusError}
              isLoading={isLoading}
            />
          </Box>
          <Box minWidth="250px">
            <TargetStorageSummaryList type={type} meta={meta} isLoading={isLoading} />
          </Box>
          <Box minWidth="250px">
            <FilesSummaryList filePaths={files} isLoading={isLoading} />
          </Box>
        </Box>
      </PageContentWrapper>
    </>
  );
};

export default BIExport;
