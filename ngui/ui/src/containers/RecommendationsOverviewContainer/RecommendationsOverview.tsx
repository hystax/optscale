import { Grid } from "@mui/material";
import Stack from "@mui/material/Stack";
import { Box } from "@mui/system";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import SearchInput from "components/SearchInput";
import { intl } from "translations/react-intl-config";
import { SPACING_2 } from "utils/layouts";
import Cards from "./Cards";
import { RecommendationsFilter, ServicesFilter, VIEW_CARDS, VIEW_TABLE, View, categoryFilter, serviceFilter } from "./Filters";
import { ACTIVE } from "./recommendations/BaseRecommendation";
import useStyles from "./RecommendationsOverview.styles";
import RecommendationsTable from "./RecommendationsTable";
import Summary from "./Summary";

const searchFilter = (search) => (recommendation) => {
  if (!search) {
    return true;
  }

  const commonMessageValues = {
    strong: (chunks) => chunks,
    link: (chunks) => chunks
  };

  const description = intl
    .formatMessage(
      { id: recommendation.descriptionMessageId },
      { ...recommendation.descriptionMessageValues, ...commonMessageValues }
    )
    .toLocaleLowerCase();

  const title = intl.formatMessage({ id: recommendation.title }).toLocaleLowerCase();

  const searchLowerCase = search.toLocaleLowerCase();

  return title.includes(searchLowerCase) || description.includes(searchLowerCase);
};

const sortRecommendation = (recommendationA, recommendationB) => {
  const aHasSavings = recommendationA.hasSaving;
  const bHasSavings = recommendationB.hasSaving;

  // Case 1: Both recommendations have their own savings - sort by saving value
  if (aHasSavings && bHasSavings) {
    return recommendationB.saving - recommendationA.saving;
  }
  // Case 2: Only recommendationA has savings, and B doesn't have it - do not change the order (place A before B)
  if (aHasSavings && !bHasSavings) {
    return -1;
  }
  // Case 3: Only recommendationB has savings, and A doesn't have it - place B before A
  if (!aHasSavings && bHasSavings) {
    return 1;
  }
  // Case 4: Both recommendations have no savings - sort them by count
  return recommendationB.count - recommendationA.count;
};

const RecommendationsOverview = ({
  isDataReady,
  recommendationClasses,
  recommendationsData,
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
  downloadLimit,
  isDownloadAvailable,
  isGetIsDownloadAvailableLoading,
  selectedDataSources,
  lastCompleted,
  totalSaving,
  nextRun,
  lastRun
}) => {
  const { classes } = useStyles();
  const checkDone = lastCompleted !== 0;

  const recommendations = Object.values(recommendationClasses)
    .map((RecommendationClass) => new RecommendationClass(ACTIVE, recommendationsData))
    .filter(categoryFilter(category))
    .filter(serviceFilter(service))
    .filter(searchFilter(search))
    .sort(sortRecommendation);

  return (
    <Stack spacing={SPACING_2}>
      <div>
        <Summary
          totalSaving={totalSaving}
          nextRun={nextRun}
          lastCompleted={lastCompleted}
          lastRun={lastRun}
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
