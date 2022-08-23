const colorizeChartLinesAndLegend = (linesAndMarkers, colors) =>
  linesAndMarkers.map(({ line, marker }, index) => {
    const color = colors[index % colors.length];
    return {
      line: {
        ...line,
        color
      },
      marker: {
        ...marker,
        color
      }
    };
  });

const getLines = (linesAndMarkers) => linesAndMarkers.map(({ line }) => line);
const getMarkers = (linesAndMarkers) => linesAndMarkers.map(({ marker }) => marker);

const getColorizedMetricChartLinesAndLegend = (linesWithMarkers, colors) => {
  const colorizedLinesAndLegend = colorizeChartLinesAndLegend(linesWithMarkers, colors);

  return {
    lines: getLines(colorizedLinesAndLegend),
    legend: getMarkers(colorizedLinesAndLegend)
  };
};

export default getColorizedMetricChartLinesAndLegend;
