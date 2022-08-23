import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, resource, resourceLocation, size } from "utils/columns";
import { RECOMMENDATION_INSTANCE_SUBSCRIPTION, INSTANCE_SUBSCRIPTION_TYPE, FORMATTED_MONEY_TYPES } from "utils/constants";
import RecommendationFactory from "../RecommendationFactory";

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
        headerDataTestId: "lbl_is_resource",
        accessor: "cloud_resource_id"
      }),
      resourceLocation({
        headerDataTestId: "lbl_is_location"
      }),
      size({
        headerDataTestId: "lbl_is_size"
      }),
      detectedAt({ headerDataTestId: "lbl_is_detected_at" }),
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_is_monthly_saving">
            <FormattedMessage id="monthlySavingsWithOneMonthSubscription" />
          </TextWithDataTestId>
        ),
        accessor: "monthly_saving",
        defaultSort: "desc",
        Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_is_annually_monthly_saving">
            <FormattedMessage id="monthlySavingsWithAnnualSubscription" />
          </TextWithDataTestId>
        ),
        accessor: "annually_monthly_saving",
        Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />
      }
    ];
  }
}

export default new InstanceSubscriptionRecommendation();
