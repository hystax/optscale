import { useTheme } from "@mui/material";
import Typography from "@mui/material/Typography";
import { useIntl } from "react-intl";
import BreakdownLabel from "components/BreakdownLabel";
import CircleLabel from "components/CircleLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import LineChart from "components/LineChart";
import { useIsOrganizationWeekend } from "hooks/useIsOrganizationWeekend";
import { useShowWeekends } from "hooks/useShowWeekends";
import { getLength } from "utils/arrays";
import { useRenderWeekendsHighlightLayer } from "./Layer";

const ChartTooltip = ({ points: allPoints, isOrganizationWeekend, breakdownBy }) => {
  const intl = useIntl();
  const theme = useTheme();

  const stringDate = allPoints[0]?.data?.x;
  const totalCount = allPoints[0]?.data?.yStacked;

  if (stringDate === undefined || totalCount === undefined) {
    return null;
  }

  const getTitleText = () => {
    const total = intl.formatMessage({ id: "total{date}" }, { date: stringDate });
    const weekend = isOrganizationWeekend(new Date(stringDate))
      ? `(${intl.formatMessage({ id: "weekend" }).toLowerCase()})`
      : "";

    return [total, weekend].filter(Boolean).join(" ");
  };

  const titleText = getTitleText();

  const renderTotalLabel = () =>
    getLength(allPoints) > 1 ? (
      <KeyValueLabel keyText={titleText} value={totalCount} gutterBottom />
    ) : (
      <Typography gutterBottom>{titleText}</Typography>
    );

  return (
    <>
      {renderTotalLabel()}
      {allPoints.map(({ id: pointId, serieColor, data: pointData = {} }) => (
        <KeyValueLabel
          key={pointId}
          gutterBottom
          keyText={
            <CircleLabel
              figureColor={serieColor}
              label={pointData.translatedSerieId ?? <BreakdownLabel breakdownBy={breakdownBy} details={pointData.details} />}
              textFirst={false}
            />
          }
          value={
            <>
              <span
                style={{
                  marginRight: theme.spacing(0.5)
                }}
              >
                {pointData.y}
              </span>
              {pointData.details.created !== 0 && (
                <span
                  style={{
                    color: theme.palette.success.main,
                    marginRight: pointData.details.deletedDayBefore !== 0 ? theme.spacing(0.5) : 0
                  }}
                >
                  +{pointData.details.created}
                </span>
              )}
              {pointData.details.deletedDayBefore !== 0 && (
                <span style={{ color: theme.palette.error.main }}>-{pointData.details.deletedDayBefore}</span>
              )}
            </>
          }
        />
      ))}
    </>
  );
};

const ResourceCountBreakdownLineChart = ({ data, colors, isLoading, style, breakdownBy, dataTestId }) => {
  const isOrganizationWeekend = useIsOrganizationWeekend();

  const { showWeekends } = useShowWeekends();

  const renderWeekendsHighlightLayer = useRenderWeekendsHighlightLayer();

  return (
    <LineChart
      dataTestId={dataTestId}
      data={data}
      yScale={{
        stacked: true
      }}
      style={style}
      colors={({ id }) => colors[id]}
      isLoading={isLoading}
      renderTooltipBody={({ slice = {} }) => {
        const { points: allPoints = [] } = slice;
        return <ChartTooltip points={allPoints} isOrganizationWeekend={isOrganizationWeekend} breakdownBy={breakdownBy} />;
      }}
      overlayLayers={
        showWeekends
          ? [
              {
                key: "weekendHighlight",
                renderCanvasContent: renderWeekendsHighlightLayer
              }
            ]
          : []
      }
    />
  );
};

export default ResourceCountBreakdownLineChart;
