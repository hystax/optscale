import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, resource, resourceLocation, size } from "utils/columns";
import { RECOMMENDATION_INSTANCE_SUBSCRIPTION, INSTANCE_SUBSCRIPTION_TYPE, FORMATTED_MONEY_TYPES } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class InstanceSubscriptionRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_INSTANCE_SUBSCRIPTION;

  moduleName = INSTANCE_SUBSCRIPTION_TYPE;

  withExclusions = true;

  messageId = "instanceSubscriptionSavingOpportunitiesTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      descriptionMessageId: "instanceSubscriptionDescription",
      emptyMessageId: "noInstanceSubscription",
      dataTestIds: {
        listTestId: "sp_instance_subscription",
        textTestId: "p_instance_subscription",
        buttonTestIds: ["btn_is_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_is_resource"
      }),
      resourceLocation({
        headerDataTestId: "lbl_is_location"
      }),
      size({
        headerDataTestId: "lbl_is_size"
      }),
      detectedAt({ headerDataTestId: "lbl_is_detected_at" }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_is_monthly_saving">
            <FormattedMessage id="monthlySavingsWithOneMonthSubscription" />
          </TextWithDataTestId>
        ),
        accessorKey: "monthly_saving",
        defaultSort: "desc",
        cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_is_annually_monthly_saving">
            <FormattedMessage id="monthlySavingsWithAnnualSubscription" />
          </TextWithDataTestId>
        ),
        accessorKey: "annually_monthly_saving",
        cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
      }
    ];
  }
}

export default new InstanceSubscriptionRecommendation();
