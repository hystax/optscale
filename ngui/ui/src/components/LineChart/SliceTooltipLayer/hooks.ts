import { useMemo } from "react";
import type { InferY, InferX, Point, ComputedSeries, LineSeries, PointColorContext, SliceData } from "@nivo/line";

export const usePoints = <Series extends LineSeries>({
  series,
  getPointColor,
  getPointBorderColor,
  formatX,
  formatY,
}: {
  series: ComputedSeries<Series>[];
  getPointColor: (context: PointColorContext<Series>) => string;
  getPointBorderColor: (point: Omit<Point<Series>, "borderColor">) => string;
  formatX: (x: InferX<Series>) => string;
  formatY: (y: InferY<Series>) => string;
}) =>
  useMemo(
    () =>
      series.reduce(
        (acc, seriesItem, seriesIndex) => [
          ...acc,
          ...seriesItem.data
            .filter((datum) => datum.position.x !== null && datum.position.y !== null)
            .map((datum, indexInSeries) => {
              const point: Omit<Point<Series>, "color" | "borderColor"> & {
                color?: string;
                borderColor?: string;
              } = {
                id: `${seriesItem.id}.${indexInSeries}`,
                indexInSeries,
                absIndex: acc.length + indexInSeries,
                seriesIndex,
                seriesId: seriesItem.id,
                seriesColor: seriesItem.color,
                x: datum.position.x,
                y: datum.position.y,
                data: {
                  ...datum.data,
                  xFormatted: formatX(datum.data.x as InferX<Series>),
                  yFormatted: formatY(datum.data.y as InferY<Series>),
                },
              };
              point.color = getPointColor({
                series: seriesItem,
                point: point as Omit<Point<Series>, "color" | "borderColor">,
              });
              point.borderColor = getPointBorderColor(point as Omit<Point<Series>, "borderColor">);

              return point as Point<Series>;
            }),
        ],
        [] as Point<Series>[]
      ),
    [series, getPointColor, getPointBorderColor, formatX, formatY]
  );

export const useSlices = <Series extends LineSeries>({
  enableSlices,
  points,
  width,
  height,
}: {
  enableSlices: boolean;
  points: Point<Series>[];
  width: number;
  height: number;
}) =>
  useMemo(() => {
    if (enableSlices === false) {
      return [];
    }

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
          points: slicePoints.reverse(),
        } as SliceData<Series>;
      });
  }, [enableSlices, height, points, width]);
