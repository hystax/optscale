import { isEmpty as isEmptyArray, isArrayOfArrays } from "utils/arrays";
import { formatRunFullName } from "utils/ml";

export const DIMENSION_GROUPS = Object.freeze({
  RUN_NAMES: "runNames",
  HYPERPARAMETERS: "hyperparameters",
  GOALS: "goals"
});

export const HEIGHT = 350;

export const MARGIN = Object.freeze({
  TOP: 50,
  BOTTOM: 40,
  LEFT: 160,
  RIGHT: 60
});

const CHART_AREA_HEIGH = HEIGHT - MARGIN.TOP - MARGIN.BOTTOM;

/**
 * This value serves as a fallback when the API does not provide the goal/hyperparameter value.
 * For instance, if it was not sent by the api.
 */
export const PARAMETER_FALLBACK_VALUE = 0;

export const FONT_SIZE = 14;

export const getChartRunsData = (runs) =>
  runs.map(({ hyperparameters, reached_goals: reachedGoals, name: runName, number: runNumber, index, color }) => ({
    runName: formatRunFullName(runNumber, runName),
    runNumber,
    reachedGoals,
    hyperparameters: Object.fromEntries(
      Object.entries(hyperparameters).map(([name, value]) => [name, value ?? PARAMETER_FALLBACK_VALUE])
    ),
    index,
    color
  }));

const doTickLabelsIntersect = (labelACoordinates, labelBCoordinates) => {
  const [labelAStart, labelAEnd] = labelACoordinates;
  const [labelBStart, lineBEnd] = labelBCoordinates;

  if (labelAEnd < labelBStart || lineBEnd < labelAStart) {
    return false;
  }

  return true;
};

const getRunNameLabelCoordinates = (runIndex, runsCount) => {
  const labelHeight = FONT_SIZE;
  const chartAreaHeight = CHART_AREA_HEIGH;

  const startCoordinate = (runIndex / runsCount) * chartAreaHeight;
  const endCoordinate = startCoordinate + labelHeight;

  return [startCoordinate, endCoordinate];
};

export const getRunNamesDimensionTicks = ({ chartRunsData, selectedChartRunsData }) => {
  if (isEmptyArray(selectedChartRunsData)) {
    return {
      // tickvals and ticktext must be applied together
      tickvals: chartRunsData.map((d) => d.index),
      // Using "" ticktext values in order to hide ticks from the chart
      ticktext: chartRunsData.map(() => "")
    };
  }

  const getNotIntersectingLabelNames = () => {
    const getRunName = (pointer) => selectedChartRunsData[pointer].runName;

    let pointerA = selectedChartRunsData.length - 1;
    let pointerB;

    const notIntersectingLabelNames = [getRunName(pointerA)];

    for (pointerB = selectedChartRunsData.length - 2; pointerB >= 0; pointerB -= 1) {
      if (
        !doTickLabelsIntersect(
          getRunNameLabelCoordinates(selectedChartRunsData[pointerA].index, chartRunsData.length),
          getRunNameLabelCoordinates(selectedChartRunsData[pointerB].index, chartRunsData.length)
        )
      ) {
        notIntersectingLabelNames.push(getRunName(pointerB));
        pointerA = pointerB;
      }
    }

    return notIntersectingLabelNames;
  };

  const notIntersectingLabelNames = getNotIntersectingLabelNames();

  return {
    /**
     * In order ticks to be clickable their values should be explicitly defined so we keep all data indexes as tickvals
     */
    tickvals: chartRunsData.map((d) => d.index),
    /**
     * Show only ticks that have do not overlap with other ticks
     */
    ticktext: chartRunsData.map(({ runName }, i) => {
      if (notIntersectingLabelNames.includes(runName)) {
        return runName;
      }
      /**
       * Show placeholders for ticks that overlap with other ticks
       * Just an empty string cannot be used since the chart would collapse it to a single element
       * So there is little hack to show a string consisting (i+1) spaces
       */
      return Array(i + 1).join(" ");
    })
  };
};

export const getSelectedRuns = (data, runsCorrelationsTraceDimensions) => {
  const getConstraintsRange = (dimensionGroup) =>
    runsCorrelationsTraceDimensions
      .filter((traceDimension) => traceDimension.dimensionGroup === dimensionGroup)
      .map(({ dimensionName, constraintrange }) => {
        const range = constraintrange ?? [];
        return {
          dimensionName,
          range: isArrayOfArrays(range) ? range : [range]
        };
      });

  const checkRanges = (ranges, getValue) => {
    if (isEmptyArray(ranges)) {
      return true;
    }

    return ranges.every(({ dimensionName, range }) => {
      if (isEmptyArray(range)) {
        return true;
      }

      const value = getValue(dimensionName);

      return range.some(([min, max]) => min <= value && value <= max);
    });
  };

  return data
    .filter((run) => checkRanges(getConstraintsRange(DIMENSION_GROUPS.RUN_NAMES), () => run.index))
    .filter((run) =>
      checkRanges(
        getConstraintsRange(DIMENSION_GROUPS.HYPERPARAMETERS),
        (accessor) => run.hyperparameters[accessor] ?? PARAMETER_FALLBACK_VALUE
      )
    )
    .filter((run) =>
      checkRanges(
        getConstraintsRange(DIMENSION_GROUPS.GOALS),
        (accessor) => run.reachedGoals[accessor]?.value ?? PARAMETER_FALLBACK_VALUE
      )
    );
};

export const getParametersDimensions = (dimensions) =>
  dimensions.filter(({ dimensionGroup }) =>
    [DIMENSION_GROUPS.GOALS, DIMENSION_GROUPS.HYPERPARAMETERS].includes(dimensionGroup)
  );
