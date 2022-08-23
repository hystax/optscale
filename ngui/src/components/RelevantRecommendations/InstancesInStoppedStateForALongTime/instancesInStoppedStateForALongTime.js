import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import {
  RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME,
  INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME_TYPE,
  FORMATTED_MONEY_TYPES
} from "utils/constants";
import { EN_FULL_FORMAT, unixTimestampToDateTime } from "utils/datetime";
import RecommendationFactory from "../RecommendationFactory";

class InstancesInStoppedStateForALongTimeRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME;

  moduleName = INSTANCES_IN_STOPPED_STATE_FOR_A_LONG_TIME_TYPE;

  withExclusions = true;

  messageId = "instancesAreStoppedButNotDeallocatedTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      descriptionMessageId: "instancesInStoppedStateForALongTimeDescription",
      emptyMessageId: "noInstanceMigrationsInStoppedState",
      dataTestIds: {
        listTestId: "sp_instances_not_deallocated",
        textTestId: "p_instances_not_deallocated",
        buttonTestIds: ["btn_ind_download", "btn_ind_cleanup_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_ind_resource",
        accessor: "cloud_resource_id"
      }),
      resourceLocation({
        headerDataTestId: "lbl_ind_location"
      }),
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_ind_last_active">
            <FormattedMessage id="lastSeenActive" />
          </TextWithDataTestId>
        ),
        accessor: "last_seen_active",
        Cell: ({ cell: { value } }) =>
          value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value, EN_FULL_FORMAT)
      },
      detectedAt({ headerDataTestId: "lbl_ind_detected_at" }),
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_ind_cost">
            <FormattedMessage id="costInStoppedState" />
          </TextWithDataTestId>
        ),
        accessor: "cost_in_stopped_state",
        Cell: ({ cell: { value } }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />
      },
      possibleMonthlySavings({
        headerDataTestId: "lbl_ind_savings",
        defaultSort: "desc"
      })
    ];
  }
}

export default new InstancesInStoppedStateForALongTimeRecommendation();
