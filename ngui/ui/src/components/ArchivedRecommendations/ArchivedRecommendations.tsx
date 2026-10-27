import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import { Box, Link, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import ArchivedResourcesCountBarChart from "components/ArchivedResourcesCountBarChart";
import BarChartLoader from "components/BarChartLoader";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PageContentWrapper from "components/PageContentWrapper";
import PanelLoader from "components/PanelLoader";
import ArchivedRecommendationsDetailsContainer from "containers/ArchivedRecommendationsDetailsContainer";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import { RECOMMENDATIONS } from "urls";
import { isEmptyArray } from "utils/arrays";
import { DATE_RANGE_TYPE } from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { isEmptyObject } from "utils/objects";

const ArchivedRecommendations = ({
  onBarChartSelect,
  onTimeRangeChange,
  dateRange,
  archivedRecommendationsChartBreakdown,
  archivedRecommendationsBreakdown,
  onDownload,
  isDownloading = false,
  isChartLoading = false,
  isBreakdownLoading = false,
}) => {
  const renderArchivedResourcesCountBarChart = () => {
    if (isChartLoading) {
      return <BarChartLoader />;
    }

    if (Object.values(archivedRecommendationsChartBreakdown).every(isEmptyObject)) {
      return (
        <Typography>
          <FormattedMessage id="noArchivedRecommendationsAvailable" />
        </Typography>
      );
    }

    return (
      <Box>
        <ArchivedResourcesCountBarChart onSelect={onBarChartSelect} breakdown={archivedRecommendationsChartBreakdown} />
      </Box>
    );
  };

  const renderArchivedRecommendationsDetails = () => {
    if (isBreakdownLoading) {
      return <PanelLoader />;
    }
    if (isEmptyArray(archivedRecommendationsBreakdown)) {
      return null;
    }
    return (
      <Box>
        <ArchivedRecommendationsDetailsContainer archivedRecommendationsBreakdown={archivedRecommendationsBreakdown} />
      </Box>
    );
  };

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={RECOMMENDATIONS} component={RouterLink}>
        <FormattedMessage id="recommendations" />
      </Link>,
    ],
    title: {
      text: <FormattedMessage id="archivedRecommendations" />,
      dataTestId: "lbl_archived_recommendations",
    },
    items: [
      {
        key: "download",
        icon: <CloudDownloadOutlinedIcon />,
        messageId: "download",
        type: "button",
        action: onDownload,
        isLoading: isDownloading,
        dataTestId: "btn_download",
      },
    ],
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <Box display="flex" justifyContent="flex-end">
            <RangePickerFormContainer
              onApply={onTimeRangeChange}
              initialStartDateValue={dateRange.startDate}
              initialEndDateValue={dateRange.endDate}
              rangeType={DATE_RANGE_TYPE.ARCHIVED_RECOMMENDATIONS}
              definedRanges={getBasicRangesSet()}
            />
          </Box>
          {renderArchivedResourcesCountBarChart()}
          {renderArchivedRecommendationsDetails()}
          <Box>
            <InlineSeverityAlert messageId="archivedRecommendationsDescription" />
          </Box>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default ArchivedRecommendations;
