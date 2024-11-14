import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import { Box, Link, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import PageContentWrapper from "components/PageContentWrapper";
import PanelLoader from "components/PanelLoader";
import ArchivedRecommendationsBreakdownContainer from "containers/ArchivedRecommendationsBreakdownContainer";
import ArchivedRecommendationsDetailsContainer from "containers/ArchivedRecommendationsDetailsContainer";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import { RECOMMENDATIONS } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { DATE_RANGE_TYPE } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const ArchivedRecommendations = ({
  onBarChartSelect,
  onTimeRangeChange,
  dateRange,
  archivedRecommendationsChartBreakdown,
  archivedRecommendationsBreakdown,
  onDownload,
  isDownloading = false,
  isChartLoading = false,
  isLoading = false
}) => {
  const renderArchivedRecommendationsDetails = () => {
    if (isLoading) {
      return <PanelLoader />;
    }
    if (isEmptyArray(archivedRecommendationsBreakdown)) {
      return (
        <Typography align="center">
          <FormattedMessage id="noRecommendations" />
        </Typography>
      );
    }
    return <ArchivedRecommendationsDetailsContainer archivedRecommendationsBreakdown={archivedRecommendationsBreakdown} />;
  };

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={RECOMMENDATIONS} component={RouterLink}>
        <FormattedMessage id="recommendations" />
      </Link>
    ],
    title: {
      text: <FormattedMessage id="archivedRecommendations" />,
      dataTestId: "lbl_archived_recommendations"
    },
    items: [
      {
        key: "download",
        icon: <CloudDownloadOutlinedIcon />,
        messageId: "download",
        type: "button",
        action: onDownload,
        isLoading: isDownloading,
        dataTestId: "btn_download"
      }
    ]
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
          <Box>
            <ArchivedRecommendationsBreakdownContainer
              isLoading={isChartLoading}
              onBarChartSelect={onBarChartSelect}
              breakdown={archivedRecommendationsChartBreakdown}
            />
          </Box>
          <Box>{renderArchivedRecommendationsDetails()}</Box>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default ArchivedRecommendations;
