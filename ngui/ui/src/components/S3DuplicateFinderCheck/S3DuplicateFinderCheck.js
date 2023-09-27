import React from "react";
import { Link, Typography } from "@mui/material";
import { Stack } from "@mui/system";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import KeyValueLabel from "components/KeyValueLabel";
import PageContentWrapper from "components/PageContentWrapper";
import TypographyLoader from "components/TypographyLoader";
import { RECOMMENDATIONS, S3_DUPLICATE_FINDER } from "urls";
import { MB } from "utils/constants";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";
import { SPACING_2 } from "utils/layouts";
import { Summary } from "./components";
import DuplicatesInspector from "./components/DuplicatesInspector";

const getSortedMatrix = (matrix, buckets) => {
  const sortedBucketNames = Object.keys(matrix)
    // Sort by monthly_savings in descending order
    .sort((toBucketA, toBucketB) => {
      const { monthly_savings: toBucketAMonthlySavings } = buckets[toBucketA];
      const { monthly_savings: toBucketBMonthlySavings } = buckets[toBucketB];

      // Both are undefined, no change in order
      if (toBucketAMonthlySavings === undefined && toBucketBMonthlySavings === undefined) {
        return 0;
      }

      // Move undefined to the end
      if (toBucketAMonthlySavings === undefined) {
        return 1;
      }

      // Keep undefined at the end
      if (toBucketBMonthlySavings === undefined) {
        return -1;
      }

      return toBucketBMonthlySavings - toBucketAMonthlySavings;
    });

  return Object.fromEntries(
    sortedBucketNames.map((name) => [
      name,
      Object.fromEntries(sortedBucketNames.map((relationBucketName) => [relationBucketName, matrix[name][relationBucketName]]))
    ])
  );
};

// Merge info from stats and filters
const getBuckets = (statsBuckets, filtersBuckets) =>
  Object.fromEntries(
    Object.entries(statsBuckets).map(([name, stats]) => {
      const filterBucket = filtersBuckets.find(({ name: filterBucketName }) => filterBucketName === name) ?? {};

      return [
        name,
        {
          ...stats,
          ...filterBucket
        }
      ];
    })
  );

const S3DuplicateFinderCheck = ({ gemini: checkData, thresholds, isLoadingProps = {} }) => {
  const { isGetCheckLoading = false, isGetSettingsLoading = false } = isLoadingProps;

  const {
    created_at: createdAt = 0,
    stats = {},
    filters = {},
    status,
    last_run: lastRun,
    last_completed: lastCompleted,
    last_error: lastError
  } = checkData;

  const {
    total_objects: totalObjects = 0,
    duplicated_objects: duplicatedObjects = 0,
    duplicates_size: duplicatesSize = 0,
    monthly_savings: monthlySavings = 0,
    buckets: statsBuckets = {},
    matrix = {}
  } = stats;

  const { min_size: minSize = 0, buckets: filtersBuckets = [] } = filters;

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={RECOMMENDATIONS} component={RouterLink}>
        <FormattedMessage id="recommendations" />
      </Link>,
      <Link key={2} to={S3_DUPLICATE_FINDER} component={RouterLink}>
        <FormattedMessage id="s3DuplicateFinderTitle" />
      </Link>
    ],
    title: {
      text: format(secondsToMilliseconds(createdAt), EN_FULL_FORMAT),
      isLoading: isGetCheckLoading
    }
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            <Summary
              status={status}
              duplicateSize={duplicatesSize}
              duplicateCount={duplicatedObjects}
              lastRun={lastRun}
              lastError={lastError}
              lastCompleted={lastCompleted}
              monthlySavings={monthlySavings}
              isLoading={isGetCheckLoading}
              totalObjects={totalObjects}
            />
          </div>
          <div>
            {isGetCheckLoading ? (
              <TypographyLoader linesCount={2} />
            ) : (
              <>
                <Typography>
                  <FormattedMessage id="selectedBuckets" />
                  &#58;&nbsp;
                  <strong>{filtersBuckets.map(({ name: bucketName }) => bucketName).join(", ")}</strong>
                </Typography>
                <KeyValueLabel
                  messageId="minimumObjectSize"
                  value={<FormattedDigitalUnit value={minSize / MB} baseUnit={SI_UNITS.MEGABYTE} />}
                />
              </>
            )}
          </div>
          <div>
            <DuplicatesInspector
              buckets={getBuckets(statsBuckets, filtersBuckets)}
              matrix={getSortedMatrix(matrix, statsBuckets)}
              isLoading={isGetCheckLoading || isGetSettingsLoading}
              status={status}
              thresholds={thresholds}
            />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

S3DuplicateFinderCheck.propTypes = {
  gemini: PropTypes.object.isRequired,
  isLoadingProps: PropTypes.shape({
    isGetCheckLoading: PropTypes.bool,
    isGetSettingsLoading: PropTypes.bool
  }),
  thresholds: PropTypes.object
};

export default S3DuplicateFinderCheck;
