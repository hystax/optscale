import { FormattedMessage } from "react-intl";
import CircleLabel from "components/CircleLabel";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import ResourceUsageFormattedNumber from "components/ResourceUsageFormattedNumber";
import { intl } from "translations/react-intl-config";
import { getLength, isEmpty, splitIntoTwoChunks } from "utils/arrays";
import { FORMATTED_MONEY_TYPES, ONE_CENT } from "utils/constants";

const DISPLAYED_TOOLTIP_ITEMS = 10;

const ResourceRawExpensesChartTooltipBody = ({ slice, stacked }) => {
  const { points: allPoints } = slice;
  const [points, limitExceededPoints] = splitIntoTwoChunks(allPoints, DISPLAYED_TOOLTIP_ITEMS);

  return (
    <>
      {stacked && getLength(allPoints) > 1 ? (
        <KeyValueLabel
          text={intl.formatMessage({ id: "totalExpenses{date}" }, { date: allPoints[0]?.data?.x })}
          value={<FormattedMoney value={allPoints[0]?.data?.yStacked} type={FORMATTED_MONEY_TYPES.COMMON} />}
          typographyProps={{
            gutterBottom: true
          }}
        />
      ) : null}
      {points.map((point) => (
        <KeyValueLabel
          key={point.id}
          renderKey={() => <CircleLabel figureColor={point.serieColor} label={point.serieId} textFirst={false} />}
          value={
            <>
              <FormattedMoney value={point.data?.y} type={FORMATTED_MONEY_TYPES.COMMON} />
              {point.data.usage > 0 && point.data.usageUnit !== undefined && point.data?.y >= ONE_CENT && (
                <>
                  {" "}
                  <FormattedMessage
                    id="(value)"
                    values={{
                      value: <ResourceUsageFormattedNumber usage={point.data.usage} unit={point.data.usageUnit} />
                    }}
                  />
                </>
              )}
            </>
          }
          typographyProps={{
            gutterBottom: true
          }}
        />
      ))}
      {!isEmpty(limitExceededPoints) && (
        <KeyValueLabel
          text={intl.formatMessage({ id: "otherCategories" })}
          value={
            <FormattedMoney
              value={limitExceededPoints.reduce((sum, point) => sum + (point.data?.y ?? 0), 0)}
              type={FORMATTED_MONEY_TYPES.COMMON}
            />
          }
        />
      )}
    </>
  );
};

export default ResourceRawExpensesChartTooltipBody;
