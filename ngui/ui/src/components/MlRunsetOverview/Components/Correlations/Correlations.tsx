import { useState } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { Stack, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { Box } from "@mui/system";
import Plotly from "plotly.js-gl2d-dist-min";
import { FormattedMessage, useIntl } from "react-intl";
import createPlotlyComponent from "react-plotly.js/factory";
import Button from "components/Button";
import QuestionMark from "components/QuestionMark";
import SubTitle from "components/SubTitle";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { SPACING_1 } from "utils/layouts";
import { removeKey } from "utils/objects";
import ParametersSelector from "../ParametersSelector";
import useStyles from "./Correlations.styles";
import {
  DIMENSION_GROUPS,
  FONT_SIZE,
  HEIGHT,
  MARGIN,
  getChartRunsData,
  getParametersDimensions,
  getRunNamesDimensionTicks,
  getSelectedRuns
} from "./utils";

// https://github.com/plotly/react-plotly.js#customizing-the-plotlyjs-bundle
const Plot = createPlotlyComponent(Plotly);

const getHyperparametersValueToTickValueMap = (chartRunsData) => {
  const hyperparameterNames = Object.keys(chartRunsData[0]?.hyperparameters ?? {});

  return Object.fromEntries(
    hyperparameterNames.map((name) => {
      const hyperparameterValues = [...new Set(chartRunsData.map(({ hyperparameters }) => hyperparameters[name]))];

      const includesNotSetValue = hyperparameterValues.some((value) => value === undefined);

      const sortedValues = hyperparameterValues.toSorted((a, b) => {
        if (typeof a === "number" && typeof b === "number") {
          return a - b;
        }
        return String(a).localeCompare(String(b));
      });

      const orderedValues = includesNotSetValue
        ? [undefined, ...sortedValues.filter((value) => value !== undefined)]
        : sortedValues;

      const valueToTick = Object.fromEntries(orderedValues.map((value, index) => [value, index]));
      const tickToValue = Object.fromEntries(orderedValues.map((value, index) => [index, value]));

      return [
        name,
        {
          valueToTick,
          tickToValue
        }
      ];
    })
  );
};

const Correlations = ({ runs = [], setSelectedRunNumbers }) => {
  const chartRunsData = getChartRunsData(runs);

  const hyperparametersValueToTickValueMap = getHyperparametersValueToTickValueMap(chartRunsData);

  const hyperparameterNames = Object.keys(chartRunsData[0]?.hyperparameters ?? {}).map((name) => name);

  const goalsDefinition = chartRunsData[0]?.reachedGoals ?? {};

  const goalKeys = Object.keys(goalsDefinition).map((key) => key) ?? [];

  const getGoalNameByKey = (goalKey) => goalsDefinition[goalKey]?.name;

  const theme = useTheme();
  const intl = useIntl();
  const { classes, cx } = useStyles();

  const runNamesDimensionLabel = intl.formatMessage({ id: "runName" });

  const initializeRunNamesDimension = () => {
    const { tickvals, ticktext } = getRunNamesDimensionTicks({
      chartRunsData,
      selectedChartRunsData: chartRunsData
    });

    return {
      label: runNamesDimensionLabel,
      dimensionName: runNamesDimensionLabel,
      dimensionGroup: DIMENSION_GROUPS.RUN_NAMES,
      tickvals,
      ticktext,
      values: chartRunsData.map((d) => d.index)
    };
  };

  const initializeHyperparameterDimension = (hyperparameterName) => {
    const hyperparameterValues = chartRunsData.map((d) => d.hyperparameters[hyperparameterName]);

    const tickvals = Object.keys(hyperparametersValueToTickValueMap[hyperparameterName].tickToValue).map(Number);

    const ticktext = tickvals.map(
      (value) => hyperparametersValueToTickValueMap[hyperparameterName].tickToValue[value] ?? "(not set)"
    );

    const values = hyperparameterValues.map(
      (value) => hyperparametersValueToTickValueMap[hyperparameterName].valueToTick[value]
    );

    return {
      label: `${hyperparameterName} (${intl.formatMessage({ id: "hyperparameterAbbreviation" })})`,
      dimensionName: hyperparameterName,
      dimensionGroup: DIMENSION_GROUPS.HYPERPARAMETERS,
      tickvals,
      ticktext,
      values
    };
  };

  const initializeGoalDimension = (goalKey) => ({
    label: getGoalNameByKey(goalKey),
    dimensionName: goalKey,
    dimensionGroup: DIMENSION_GROUPS.GOALS,
    values: chartRunsData.map((run) => {
      const { value = 0 } = run.reachedGoals?.[goalKey] ?? {};

      return value;
    })
  });

  /**
   * Keep dimensions in the state
   * 1. to be able to update ticks for run names dimension
   * 2. to be able to identify which dimensions are currently selected
   *
   * https://github.com/plotly/react-plotly.js#state-management
   */
  const [dimensionsState, setDimensionsState] = useState(() => {
    const runNamesDimension = initializeRunNamesDimension();

    const hyperparameterDimensions = hyperparameterNames.map(initializeHyperparameterDimension);

    const goalDimensions = goalKeys.map(initializeGoalDimension);

    return [runNamesDimension, ...hyperparameterDimensions, ...goalDimensions];
  });

  const clearFilters = () => {
    setDimensionsState((currentDimensionsState) =>
      currentDimensionsState.map((dimension) => removeKey(dimension, "constraintrange"))
    );
  };

  const isSomethingSelected = dimensionsState.some(
    (dimension) => !!dimension.constraintrange && !isEmptyArray(dimension.constraintrange)
  );

  return (
    <Stack spacing={SPACING_1}>
      <Stack direction="row" spacing={0} alignItems="center" height="30px">
        <SubTitle sx={{ mr: 1 }}>
          <FormattedMessage id="correlations" />
        </SubTitle>
        <QuestionMark
          tooltipText={<FormattedMessage id="correlationsChartHint" />}
          fontSize="small"
          Icon={InfoOutlinedIcon}
          withLeftMargin={false}
        />
        {[hyperparameterNames, goalKeys].every(isEmptyArray) ? null : (
          <ParametersSelector
            hyperparametersDimensionsNames={hyperparameterNames}
            goalDimensionsNames={goalKeys}
            getGoalDimensionName={(k) => getGoalNameByKey(k)}
            selected={getParametersDimensions(dimensionsState).map(({ dimensionName }) => dimensionName)}
            onChange={(newSelected) => {
              setDimensionsState(([runNamesDimension, ...restDimensions]) => {
                const selectedDimensions = [...hyperparameterNames, ...goalKeys]
                  .filter((name) => newSelected.includes(name))
                  .map((selectedParameter) => {
                    const existingDimension = restDimensions.find(({ dimensionName }) => dimensionName === selectedParameter);
                    if (existingDimension) {
                      return existingDimension;
                    }
                    if (hyperparameterNames.includes(selectedParameter)) {
                      return initializeHyperparameterDimension(selectedParameter);
                    }
                    return initializeGoalDimension(selectedParameter);
                  });

                return [runNamesDimension, ...selectedDimensions];
              });
            }}
          />
        )}
        {isSomethingSelected && (
          <Button
            color="error"
            messageId="clearFilters"
            dashedBorder
            onClick={clearFilters}
            startIcon={<DeleteOutlinedIcon />}
            customClass={classes.clearFiltersButton}
          />
        )}
      </Stack>
      <Box height={`${HEIGHT}px`}>
        {isEmptyArray(chartRunsData) ? (
          <Typography
            textAlign="center"
            component="div"
            height="100%"
            display="flex"
            justifyContent="center"
            alignItems="center"
          >
            <FormattedMessage id="noDataToDisplay" />
          </Typography>
        ) : (
          <div className={cx(classes.wrapper, classes.fullWidthHeight)}>
            <Plot
              onInitialized={(figure) => {
                const [runsCorrelationsTrace] = figure.data;
                const { dimensions } = runsCorrelationsTrace;
                const selectedRuns = getSelectedRuns(chartRunsData, dimensions, hyperparametersValueToTickValueMap);

                setSelectedRunNumbers(selectedRuns.map(({ runNumber }) => runNumber));

                setDimensionsState(dimensions);
              }}
              onUpdate={(figure) => {
                const [runsCorrelationsTrace] = figure.data;
                const { dimensions } = runsCorrelationsTrace;

                const selectedRuns = getSelectedRuns(chartRunsData, dimensions, hyperparametersValueToTickValueMap);

                const updateRunNamesDimensionTicks = () => {
                  const { tickvals, ticktext } = getRunNamesDimensionTicks({
                    chartRunsData,
                    selectedChartRunsData: selectedRuns
                  });

                  const [runsDimension, ...restDimensions] = dimensions;

                  const updatedRunsDimension = {
                    ...runsDimension,
                    tickvals,
                    ticktext
                  };

                  return [updatedRunsDimension, ...restDimensions];
                };

                const newDimensionState = updateRunNamesDimensionTicks();

                /**
                 * Comparing states in order to prevent infinite updates loop
                 *
                 * TODO: Investigate if it is possible to update local state and prevent infinite updates
                 * The problem is that the onUpdate callback is called on each component update, so if
                 * we update the state here we get an infinite update loop
                 */
                if (JSON.stringify(dimensionsState) !== JSON.stringify(newDimensionState)) {
                  setSelectedRunNumbers(selectedRuns.map(({ runNumber }) => runNumber));
                  setDimensionsState(updateRunNamesDimensionTicks());
                }
              }}
              data={[
                {
                  type: "parcoords",
                  dimensions: dimensionsState,
                  line: {
                    // https://plotly.com/javascript/reference/parcoords/#parcoords-line-color
                    color: chartRunsData.map(({ index }) => index),
                    // https://plotly.com/javascript/reference/parcoords/#parcoords-line-colorscale
                    colorscale:
                      chartRunsData.length === 1
                        ? [
                            [0, chartRunsData[0].color],
                            [1, chartRunsData[0].color]
                          ]
                        : chartRunsData.map(({ index, color }) => [
                            chartRunsData.length === 1 ? 0 : index / (chartRunsData.length - 1),
                            color
                          ])
                  }
                }
              ]}
              layout={{
                margin: {
                  l: MARGIN.LEFT,
                  t: MARGIN.TOP,
                  b: MARGIN.BOTTOM,
                  r: MARGIN.RIGHT
                },
                font: {
                  color: theme.palette.text.primary,
                  family: theme.typography.fontFamily,
                  size: FONT_SIZE
                }
              }}
              frames={[]}
              config={{
                displayModeBar: true,
                displaylogo: false,
                responsive: true,
                modeBarButtonsToRemove: ["toImage"]
              }}
              className={classes.fullWidthHeight}
            />
          </div>
        )}
      </Box>
    </Stack>
  );
};

export default Correlations;
