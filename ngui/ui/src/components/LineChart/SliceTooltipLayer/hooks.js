import { useMemo } from "react";

export const usePoints = ({ series, getPointColor, getPointBorderColor, formatX, formatY }) =>
  useMemo(
    () =>
      series.reduce(
        (acc, serie) => [
          ...acc,
          ...serie.data
            .filter(({ position: { x, y } }) => x !== null && y !== null)
            .map((datum, i) => {
              const point = {
                id: `${serie.id}.${i}`,
                index: acc.length + i,
                serieId: serie.id,
                serieColor: serie.color,
                x: datum.position.x,
                y: datum.position.y
              };
              point.color = getPointColor(serie);
              point.borderColor = getPointBorderColor(point);
              point.data = {
                ...datum.data,
                xFormatted: formatX(datum.data.x),
                yFormatted: formatY(datum.data.y)
              };

              return point;
            })
        ],
        []
      ),
    [series, getPointColor, getPointBorderColor, formatX, formatY]
  );

export const useSlices = ({ enableSlices, points, width, height }) =>
  useMemo(() => {
    if (enableSlices === false) return [];

    const map = new Map();

    points.forEach((point) => {
      if (point.data.x === null || point.data.y === null) {
        return;
      }
      if (!map.has(point.x)) {
        map.set(point.x, [point]);
      } else {
        map.get(point.x).push(point);
      }
    });

    return Array.from(map.entries())
      .sort((a, b) => a[0] - b[0])
      .map(([x, slicePoints], i, slices) => {
        const prevSlice = slices[i - 1];
        const nextSlice = slices[i + 1];

        let x0;
        if (!prevSlice) {
          x0 = x;
        } else {
          x0 = x - (x - prevSlice[0]) / 2;
        }

        let sliceWidth;
        if (!nextSlice) {
          sliceWidth = width - x0;
        } else {
          sliceWidth = x - x0 + (nextSlice[0] - x) / 2;
        }

        return {
          id: x,
          x0,
          x,
          y0: 0,
          y: 0,
          width: sliceWidth,
          height,
          points: slicePoints.reverse()
        };
      });
  }, [enableSlices, height, points, width]);
