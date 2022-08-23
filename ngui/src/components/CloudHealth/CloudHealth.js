import React, { useMemo } from "react";
import Battery30OutlinedIcon from "@mui/icons-material/Battery30Outlined";
import Battery60OutlinedIcon from "@mui/icons-material/Battery60Outlined";
import BatteryFullOutlinedIcon from "@mui/icons-material/BatteryFullOutlined";
import HomeOutlinedIcon from "@mui/icons-material/HomeOutlined";
import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormGroup from "@mui/material/FormGroup";
import Grid from "@mui/material/Grid";
import { useTheme } from "@mui/material/styles";
import Switch from "@mui/material/Switch";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import { useDispatch } from "react-redux";
import ActionBar from "components/ActionBar";
import CheckboxLoader from "components/CheckboxLoader";
import CloudLabel from "components/CloudLabel";
import HeaderHelperCell from "components/HeaderHelperCell";
import IconLabelGrid from "components/IconLabelGrid";
import PageContentWrapper from "components/PageContentWrapper";
import SummaryGrid from "components/SummaryGrid";
import SwitchLoader from "components/SwitchLoader";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import Tooltip from "components/Tooltip";
import WrapperCard from "components/WrapperCard";
import { useRootData } from "hooks/useRootData";
import { hasIntersection, isEmpty } from "utils/arrays";
import {
  CLOUD_HEALTH_TYPES,
  BEST_OVERALL_REGION,
  CHEAPEST_FROM_TOP_FIVE_REGION,
  BEST_AVAILABILITY_ZONE,
  BEST_FOR_NEW_WORKLOADS,
  BEST_FOR_EXISTING_WORKLOADS_SCALING,
  BEST_FOR_SPOT,
  CLOUD_HEALTH_SCORES,
  CLOUD_HEALTH_DOMESTIC_REGIONS,
  AWS_CNR,
  AZURE_CNR,
  SUCCESS,
  WARNING,
  ERROR
} from "utils/constants";
import { SPACING_1, SPACING_2 } from "utils/layouts";
import { sortByValue } from "utils/objects";
import { toggleDomesticRegionsSwitch, toggleCloudTypeCheckboxes } from "./actionCreators";
import useStyles from "./CloudHealth.styles";
import { CLOUD_HEALTH } from "./reducer";

const BORDERLINE_OVERALL_SCORE = 6.0;

const extendScoresData = (scores) =>
  scores.map((score) => ({
    ...score,
    overallScore: (score.proximity + score.network_latency + 3 * score.price + score.performance_avg + score.capacity_avg) / 7
  }));

const getBaseScoreDefinition = (value) => {
  if (value <= CLOUD_HEALTH_SCORES.BASE_BOTTOM_LOW_LIMIT) {
    return {
      color: ERROR,
      priceTooltipMessageId: "expensive",
      currentUsageIcon: <Battery30OutlinedIcon style={{ transform: "rotate(90deg)" }} color="primary" />,
      currentUsageTooltipMessageId: "low"
    };
  }
  if (value <= CLOUD_HEALTH_SCORES.BASE_BOTTOM_MEDIUM_LIMIT) {
    return {
      color: WARNING,
      priceTooltipMessageId: "fair",
      currentUsageIcon: <Battery60OutlinedIcon style={{ transform: "rotate(90deg)" }} color="primary" />,
      currentUsageTooltipMessageId: "average"
    };
  }
  return {
    color: SUCCESS,
    priceTooltipMessageId: "cheap",
    currentUsageIcon: <BatteryFullOutlinedIcon style={{ transform: "rotate(90deg)" }} color="primary" />,
    currentUsageTooltipMessageId: "active"
  };
};

const getBestAz = (score = {}) => {
  const performanceScores = score.performance_scores || {};
  const capacityScores = score.capacity_scores || {};

  const azs = [...new Set([...Object.keys(performanceScores), ...Object.keys(capacityScores)])];

  const multiplicationArray = azs.reduce(
    (result, az) =>
      [...result, az].sort((a, b) => performanceScores[b] * capacityScores[b] - performanceScores[a] * capacityScores[a]),
    []
  );

  return multiplicationArray[0];
};

const getBestForExistingWorkloadsScalingRegion = (scores) =>
  scores.find(
    (score) =>
      score.proximity >= CLOUD_HEALTH_SCORES.PROXIMITY.EXISTING_WORKLOADS &&
      score.network_latency >= CLOUD_HEALTH_SCORES.NETWORK_LATENCY.EXISTING_WORKLOADS
  ) || {};

const getBestForNewWorkloadsRegion = (scores) =>
  scores.find((score) => score.price >= CLOUD_HEALTH_SCORES.PRICE.NEW_WORKLOADS) || {};

const getBestForSpotInstancesRegion = (scores) =>
  scores.find((score) => score.capacity_avg >= CLOUD_HEALTH_SCORES.CAPACITY.SPOT_INSTANCES) || {};

const getHomeRegions = (scores) => scores.filter((score) => score.proximity >= CLOUD_HEALTH_SCORES.PROXIMITY.HOME_REGION);

// TODO - in the next iteration the application will get most of the values from the backend.
// Refactor logic to avoid duplicated function calls when the final response format is defined.
const hasDomesticRegions = (scores) => {
  const homeRegions = getHomeRegions(scores).reduce((result, score) => [...result, score.region], []);
  return hasIntersection([].concat(...Object.values(CLOUD_HEALTH_DOMESTIC_REGIONS)), homeRegions);
};

const getDomesticRegions = (scores) => {
  const homeRegions = getHomeRegions(scores).reduce((result, score) => [...result, score.region], []);

  if (isEmpty(homeRegions)) {
    return [];
  }

  return Object.values(CLOUD_HEALTH_DOMESTIC_REGIONS).reduce((result, currentArray) => {
    if (hasIntersection(currentArray, homeRegions)) {
      return [...result, ...scores.filter((score) => currentArray.includes(score.region))];
    }
    return result;
  }, []);
};

const getAwsRegions = (scores) => scores.filter((score) => score.cloud_type === AWS_CNR);
const getAzureRegions = (scores) => scores.filter((score) => score.cloud_type === AZURE_CNR);

const getTableData = ({ domesticRegionsSwitchState, awsCheckboxState, azureCheckboxState, scores }) => {
  // Checkboxes filters dominate the switch
  let filteredRegions = [];

  // it is important not to break the order of scores if both switches are active
  // see https://gitlab.com/hystax/ngui/-/merge_requests/1491
  if (awsCheckboxState && azureCheckboxState) {
    filteredRegions = [...scores];
  } else if (awsCheckboxState) {
    filteredRegions = [...filteredRegions, ...getAwsRegions(scores)];
  } else if (azureCheckboxState) {
    filteredRegions = [...filteredRegions, ...getAzureRegions(scores)];
  }

  if (domesticRegionsSwitchState) {
    filteredRegions = getDomesticRegions(filteredRegions);
  }

  return filteredRegions;
};

const DomesticRegionsSwitch = ({ checked }) => {
  const { classes } = useStyles();
  const intl = useIntl();
  const dispatch = useDispatch();

  const toggle = () => dispatch(toggleDomesticRegionsSwitch());

  return (
    <FormControlLabel
      className={classes.zeroMarginLeft}
      control={
        <Tooltip title={intl.formatMessage({ id: "domesticRegionsSwitchTooltip" })}>
          <Switch checked={checked} onChange={toggle} />
        </Tooltip>
      }
      label={<Typography>{intl.formatMessage({ id: "showOnlyDomesticRegions" })}</Typography>}
      labelPlacement="start"
    />
  );
};

const CloudTypeCheckbox = ({ checked, cloudType, labelMessageId, disabled = false }) => {
  const intl = useIntl();
  const dispatch = useDispatch();

  const toggle = (type) => {
    dispatch(toggleCloudTypeCheckboxes(type));
  };

  return (
    <FormControlLabel
      control={<Checkbox checked={checked} disabled={disabled} onChange={() => toggle(cloudType)} />}
      label={<Typography>{intl.formatMessage({ id: labelMessageId })}</Typography>}
      labelPlacement="start"
    />
  );
};

const ScoreLabel = ({ az, score }) => {
  const theme = useTheme();
  return (
    /* TODO
      Badge is not suitable here, because it intends to overlap an underlying component
      We might want to create our own Badge component or update the CircleLabel or create a new(name TBD, something like FigureStatus) component.
    */
    <div style={{ display: "flex" }}>
      <div
        style={{
          backgroundColor: `${theme.palette[getBaseScoreDefinition(score).color].main}`,
          borderRadius: "10px",
          padding: "0 6px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: theme.palette.common.white,
          height: "20px",
          width: "20px",
          minHeight: "20px",
          minWidth: "20px",
          marginRight: "2px"
        }}
      >
        <Typography variant="caption">{score}</Typography>
      </div>
      <Typography variant="caption">{az}</Typography>
    </div>
  );
};

const renderScores = (scores) => (
  <Grid alignItems="center" container spacing={SPACING_1}>
    {Object.entries(sortByValue(scores, "desc")).map(([az, score]) => (
      <Grid key={az} container item xs={12}>
        <ScoreLabel key={az} az={az} score={score} />
      </Grid>
    ))}
  </Grid>
);

const actionBarDefinition = {
  title: {
    messageId: "cloudHealthTitle"
  }
};

const CloudImage = ({ scores, region, customLabel = null }) => {
  const targetScore = scores.find((score) => score.region === region) || {};
  const { cloud_type: cloudType = "" } = targetScore;
  return customLabel || region ? (
    <CloudLabel iconProps={{ fontSize: "large" }} type={cloudType} label={customLabel || region} />
  ) : null;
};

const renderCurrentUsage = (rowData, intl) => {
  const computeScore = rowData.proximity;
  const networkingScore = 0.8 * rowData.proximity;
  const storageScore = (2 * rowData.proximity) / 3;

  const computeScoreDefinition = getBaseScoreDefinition(computeScore);
  const networkingScoreDefinition = getBaseScoreDefinition(networkingScore);
  const storageScoreDefinition = getBaseScoreDefinition(storageScore);

  return (
    <>
      {computeScore >= 1 ? (
        <IconLabelGrid
          label={intl.formatMessage({ id: "compute" })}
          endIcon={
            <Tooltip title={intl.formatMessage({ id: computeScoreDefinition.currentUsageTooltipMessageId })}>
              {computeScoreDefinition.currentUsageIcon}
            </Tooltip>
          }
        />
      ) : null}
      {networkingScore >= 1 ? (
        <IconLabelGrid
          label={intl.formatMessage({ id: "networking" })}
          endIcon={
            <Tooltip title={intl.formatMessage({ id: networkingScoreDefinition.currentUsageTooltipMessageId })}>
              {networkingScoreDefinition.currentUsageIcon}
            </Tooltip>
          }
        />
      ) : null}
      {storageScore >= 1 ? (
        <IconLabelGrid
          label={intl.formatMessage({ id: "storage" })}
          endIcon={
            <Tooltip title={intl.formatMessage({ id: storageScoreDefinition.currentUsageTooltipMessageId })}>
              {storageScoreDefinition.currentUsageIcon}
            </Tooltip>
          }
        />
      ) : null}
    </>
  );
};

const renderRecommenderFor = (rowData, intl) => (
  <>
    {rowData.price >= CLOUD_HEALTH_SCORES.PRICE.INDEPENDENT_COMPUTE ? (
      <>
        <Tooltip title={intl.formatMessage({ id: "independentComputeTooltip" })}>
          <span>{intl.formatMessage({ id: "independentCompute" })}</span>
        </Tooltip>
        <br />
      </>
    ) : null}
    {rowData.proximity >= CLOUD_HEALTH_SCORES.PROXIMITY.COMPUTE_SCALING &&
    rowData.network_latency >= CLOUD_HEALTH_SCORES.NETWORK_LATENCY.COMPUTE_SCALING ? (
      <>
        <Tooltip title={intl.formatMessage({ id: "computeScalingTooltip" })}>
          <span>{intl.formatMessage({ id: "computeScaling" })}</span>
        </Tooltip>
        <br />
      </>
    ) : null}
    {rowData.proximity >= CLOUD_HEALTH_SCORES.PROXIMITY.DATA_STORAGE &&
    rowData.price >= CLOUD_HEALTH_SCORES.PRICE.DATA_STORAGE ? (
      <>
        <Tooltip title={intl.formatMessage({ id: "dataStorageTooltip" })}>
          <span>{intl.formatMessage({ id: "dataStorage" })}</span>
        </Tooltip>
        <br />
      </>
    ) : null}
    {rowData.capacity_avg >= CLOUD_HEALTH_SCORES.CAPACITY.SPOT_INSTANCES ? (
      <>
        <Tooltip title={intl.formatMessage({ id: "spotInstancesTooltip" })}>
          <span>{intl.formatMessage({ id: "spotInstances" })}</span>
        </Tooltip>
        <br />
      </>
    ) : null}
  </>
);

const CloudHealth = ({ isLoading, data = {} }) => {
  const intl = useIntl();
  const theme = useTheme();

  const {
    rootData: {
      domesticRegionsSwitchState,
      cloudTypeCheckboxesState: { [AWS_CNR]: awsCheckboxState = true, [AZURE_CNR]: azureCheckboxState = true } = {}
    } = {}
  } = useRootData(CLOUD_HEALTH);

  // TODO - add a coefficient based in max_value.
  // At this point it equals 10, but if it changes, the application should keep 10-based scoring.
  const { cheapest_top_five_region: cheapestFromTopFiveRegion = "", region_scores: scores = [] } = data;

  const extendedScores = extendScoresData(scores).sort((a, b) => b.overallScore - a.overallScore);
  const showDomesticSwitch = hasDomesticRegions(extendedScores);

  // Calculate only 5 cards out of 6, take 1 of them directly from the API(cheapest from top 5)
  const bestAz = getBestAz(extendedScores[0]);

  const { region: bestOverallRegionRegion = "" } = extendedScores[0] || {};

  const { region: bestForExistingWorkloadsScalingRegion = "" } = getBestForExistingWorkloadsScalingRegion(extendedScores);

  const { region: bestForNewWorkloadsRegion = "" } = getBestForNewWorkloadsRegion(extendedScores);

  const { region: bestForSpotInstancesRegion = "" } = getBestForSpotInstancesRegion(extendedScores);

  const summaryDataRow1 = [
    {
      key: BEST_OVERALL_REGION,
      value: <CloudImage scores={scores} region={bestOverallRegionRegion} />,
      captionMessageId: CLOUD_HEALTH_TYPES[BEST_OVERALL_REGION],
      help: {
        show: true,
        messageId: "bestOverallScoredRegionDescription"
      },
      isLoading
    },
    {
      key: CHEAPEST_FROM_TOP_FIVE_REGION,
      value: <CloudImage scores={scores} region={cheapestFromTopFiveRegion} />,
      help: {
        show: true,
        messageId: "cheapestRegionFromTopFiveDescription"
      },
      captionMessageId: CLOUD_HEALTH_TYPES[CHEAPEST_FROM_TOP_FIVE_REGION],
      isLoading
    },
    {
      key: BEST_AVAILABILITY_ZONE,
      value: <CloudImage scores={scores} region={bestOverallRegionRegion} customLabel={bestAz} />,
      help: {
        show: true,
        messageId: "bestScoredAvailabilityZoneDescription"
      },
      captionMessageId: CLOUD_HEALTH_TYPES[BEST_AVAILABILITY_ZONE],
      isLoading
    }
  ];

  const summaryDataRow2 = [
    {
      key: BEST_FOR_EXISTING_WORKLOADS_SCALING,
      value: <CloudImage scores={scores} region={bestForExistingWorkloadsScalingRegion} />,
      help: {
        show: true,
        messageId: "bestForExistingWorkLoadsScalingDescription"
      },
      captionMessageId: CLOUD_HEALTH_TYPES[BEST_FOR_EXISTING_WORKLOADS_SCALING],
      isLoading
    },
    {
      key: BEST_FOR_NEW_WORKLOADS,
      value: <CloudImage scores={scores} region={bestForNewWorkloadsRegion} />,
      help: {
        show: true,
        messageId: "bestForNewWorkLoadsDescription"
      },
      captionMessageId: CLOUD_HEALTH_TYPES[BEST_FOR_NEW_WORKLOADS],
      isLoading
    },
    {
      key: BEST_FOR_SPOT,
      value: <CloudImage scores={scores} region={bestForSpotInstancesRegion} />,
      help: {
        show: true,
        messageId: "bestForSpotInstancesDescription"
      },
      captionMessageId: CLOUD_HEALTH_TYPES[BEST_FOR_SPOT],
      isLoading
    }
  ];

  const tableDefinition = useMemo(
    () => [
      {
        Header: intl.formatMessage({ id: "region" }),
        accessor: "region",
        Cell: ({ row: { original } }) => (
          <CloudLabel
            label={original.region}
            type={original.cloud_type}
            endAdornment={
              original.proximity >= CLOUD_HEALTH_SCORES.PROXIMITY.HOME_REGION && (
                <Tooltip title={intl.formatMessage({ id: "homeRegion" })}>
                  <HomeOutlinedIcon fontSize="small" />
                </Tooltip>
              )
            }
          />
        )
      },
      {
        defaultSort: "desc",
        Header: <HeaderHelperCell titleMessageId="overallScore" helperMessageId="overallScoreDescription" />,
        accessor: "overallScore",
        Cell: ({ row: { original } }) => {
          const recommendationScoreDefinition = getBaseScoreDefinition(original.overallScore);
          return (
            <span style={{ color: theme.palette[recommendationScoreDefinition.color].main, fontWeight: "bold" }}>
              {original.overallScore.toFixed(1)}
            </span>
          );
        }
      },
      {
        Header: <HeaderHelperCell titleMessageId="currentUsage" helperMessageId="currentUsageDescription" />,
        // Current usage is based on proximity, it is valid to use this field for sorting
        accessor: "proximity",
        Cell: ({ row: { original } }) => renderCurrentUsage(original, intl)
      },
      {
        Header: <HeaderHelperCell titleMessageId="recommendedFor" helperMessageId="recommendedForDescription" />,
        id: "recommendedFor",
        Cell: ({
          row: {
            original: { overallScore, ...rest }
          }
        }) => overallScore >= BORDERLINE_OVERALL_SCORE && renderRecommenderFor(rest, intl),
        isStatic: true
      },
      {
        Header: <HeaderHelperCell titleMessageId="price" helperMessageId="priceDescription" />,
        accessor: "price",
        Cell: ({ row: { original } }) => {
          const priceDefinition = getBaseScoreDefinition(original.price);
          return (
            <Tooltip title={intl.formatMessage({ id: priceDefinition.priceTooltipMessageId })}>
              <span style={{ color: theme.palette[priceDefinition.color].main, fontWeight: "bold" }}>
                {original.price.toFixed(1)}
              </span>
            </Tooltip>
          );
        }
      },
      {
        Header: <HeaderHelperCell titleMessageId="azCapacity" helperMessageId="azCapacityDescription" />,
        accessor: "capacity_avg",
        Cell: ({
          row: {
            original: { capacity_scores: capacityScores = {} }
          }
        }) => renderScores(capacityScores)
      },
      {
        Header: <HeaderHelperCell titleMessageId="azPerformance" helperMessageId="azPerformanceDescription" />,
        accessor: "performance_avg",
        Cell: ({
          row: {
            original: { performance_scores: performanceScores = {} }
          }
        }) => renderScores(performanceScores)
      }
    ],
    [intl, theme.palette]
  );

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_2}>
          <Grid item xs={12}>
            <SummaryGrid summaryData={summaryDataRow1} />
          </Grid>
          <Grid item xs={12}>
            <SummaryGrid summaryData={summaryDataRow2} />
          </Grid>
          <Grid item xs={12}>
            {isLoading ? (
              <>
                <CheckboxLoader fullWidth />
                <SwitchLoader fullWidth />
              </>
            ) : (
              <>
                <Box display="flex" alignItems="center">
                  <Typography>{intl.formatMessage({ id: "showResultsFor" })}</Typography>
                  <FormGroup row>
                    <CloudTypeCheckbox checked={awsCheckboxState} cloudType={AWS_CNR} labelMessageId="aws" />
                    <CloudTypeCheckbox checked={azureCheckboxState} cloudType={AZURE_CNR} labelMessageId="azure" />
                  </FormGroup>
                </Box>
                {showDomesticSwitch ? <DomesticRegionsSwitch checked={domesticRegionsSwitchState} /> : null}
              </>
            )}
          </Grid>
          <Grid item xs={12}>
            <WrapperCard title={<FormattedMessage id="summaryBy" values={{ name: "region" }} />}>
              {isLoading ? (
                <TableLoader columnsCounter={tableDefinition.length} showHeader />
              ) : (
                <Table
                  data={getTableData({
                    domesticRegionsSwitchState,
                    awsCheckboxState,
                    azureCheckboxState,
                    scores: extendedScores
                  })}
                  columns={tableDefinition}
                  localization={{
                    emptyMessageId: "noRegionsToScore"
                  }}
                />
              )}
            </WrapperCard>
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

ScoreLabel.propTypes = {
  az: PropTypes.string.isRequired,
  score: PropTypes.number.isRequired
};

DomesticRegionsSwitch.propTypes = {
  checked: PropTypes.bool.isRequired
};

CloudTypeCheckbox.propTypes = {
  checked: PropTypes.bool.isRequired,
  cloudType: PropTypes.string.isRequired,
  labelMessageId: PropTypes.string.isRequired,
  disabled: PropTypes.bool
};

CloudImage.propTypes = {
  scores: PropTypes.array.isRequired,
  region: PropTypes.string.isRequired,
  customLabel: PropTypes.string
};

CloudHealth.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  data: PropTypes.object
};

export default CloudHealth;
