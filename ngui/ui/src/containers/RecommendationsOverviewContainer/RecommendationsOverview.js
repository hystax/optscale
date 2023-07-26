import React from "react";
import { Grid } from "@mui/material";
import Stack from "@mui/material/Stack";
import { Box } from "@mui/system";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import SearchInput from "components/SearchInput";
import { SPACING_2 } from "utils/layouts";
import Cards from "./Cards";
import { RecommendationsFilter, ServicesFilter, VIEW_CARDS, VIEW_TABLE, View } from "./Filters";
import useStyles from "./RecommendationsOverview.styles";
import RecommendationsTable from "./RecommendationsTable";
import Summary from "./Summary";

const RecommendationsOverview = ({
  data,
  isDataReady,
  onRecommendationClick,
  riSpExpensesSummary,
  isRiSpExpensesSummaryLoading,
  setSearch,
  search,
  setCategory,
  category,
  setService,
  service,
  setView,
  view,
  recommendations,
  downloadLimit,
  isDownloadAvailable,
  isGetIsDownloadAvailableLoading,
  selectedDataSources
}) => {
  const { classes } = useStyles();
  const { last_completed: lastCompleted } = data;
  const checkDone = lastCompleted !== 0;

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <Summary
          totalSaving={data.total_saving}
          nextRun={data.next_run}
          lastCompleted={data.last_completed}
          lastRun={data.last_run}
          riSpExpensesSummary={riSpExpensesSummary}
          isLoadingProps={{
            isRecommendationsLoading: !isDataReady,
            isRiSpExpensesSummaryLoading
          }}
        />
      </div>
      <div>
        <Box className={classes.actionBar}>
          <Box className={classes.actionBarPart}>
            <div>
              <RecommendationsFilter onChange={setCategory} value={category} />
            </div>
            <div>
              <ServicesFilter onChange={setService} value={service} />
            </div>
          </Box>
          <Box className={classes.actionBarPart}>
            <View onChange={setView} value={view} />
            <SearchInput onSearch={setSearch} initialSearchText={search} />
          </Box>
        </Box>
      </div>
      <div>
        {checkDone ? (
          <>
            {view === VIEW_CARDS && (
              <Box className={classes.cardsGrid}>
                <Cards
                  recommendations={recommendations}
                  isLoading={!isDataReady}
                  downloadLimit={downloadLimit}
                  onRecommendationClick={onRecommendationClick}
                  isDownloadAvailable={isDownloadAvailable}
                  isGetIsDownloadAvailableLoading={isGetIsDownloadAvailableLoading}
                  selectedDataSources={selectedDataSources}
                />
              </Box>
            )}
            {view === VIEW_TABLE && (
              <RecommendationsTable
                recommendations={recommendations}
                isLoading={!isDataReady}
                downloadLimit={downloadLimit}
                onRecommendationClick={onRecommendationClick}
                isDownloadAvailable={isDownloadAvailable}
                isGetIsDownloadAvailableLoading={isGetIsDownloadAvailableLoading}
                selectedDataSources={selectedDataSources}
              />
            )}
          </>
        ) : (
          <Grid item xs={12}>
            <InlineSeverityAlert messageId="recommendationProceeding" />
          </Grid>
        )}
      </div>
    </Stack>
  );
};

export default RecommendationsOverview;
