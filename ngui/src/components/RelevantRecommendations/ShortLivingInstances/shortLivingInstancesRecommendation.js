import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES, RECOMMENDATION_SHORT_LIVING_INSTANCES, SHORT_LIVING_INSTANCES_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class ShortLivingInstancesRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_SHORT_LIVING_INSTANCES;

  moduleName = SHORT_LIVING_INSTANCES_TYPE;

  withExclusions = true;

  messageId = "possibleSavingsWithSpotInstancesTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      descriptionMessageId: "shortLivingInstancesDescription",
      emptyMessageId: "noNonSpotInstances",
      dataTestIds: {
        listTestId: "sp_spot_instances",
        textTestId: "p_spot_instances",
        buttonTestIds: ["btn_si_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_si_resource"
      }),
      resourceLocation({
        headerDataTestId: "lbl_si_location"
      }),
      detectedAt({ headerDataTestId: "lbl_si_detected_at" }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_si_expenses">
            <FormattedMessage id="expenses" />
          </TextWithDataTestId>
        ),
        accessorKey: "total_cost",
        cell: ({ cell }) => {
          const value = cell.getValue();

          return <FormattedMoney value={value} type={FORMATTED_MONEY_TYPES.COMMON} />;
        }
      },
      possibleMonthlySavings({
        headerDataTestId: "lbl_si_savings",
        defaultSort: "desc"
      })
    ];
  }
}

export default new ShortLivingInstancesRecommendation();
