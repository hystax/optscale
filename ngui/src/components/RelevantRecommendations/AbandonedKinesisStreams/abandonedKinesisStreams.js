import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import {
  RECOMMENDATION_ABANDONED_KINESIS_STREAMS,
  ABANDONED_KINESIS_STREAMS_TYPE,
  FORMATTED_MONEY_TYPES
} from "utils/constants";
import RecommendationFactory from "../RecommendationFactory";

class AbandonedKinesisStreamsRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_ABANDONED_KINESIS_STREAMS;

  moduleName = ABANDONED_KINESIS_STREAMS_TYPE;

  withExclusions = true;

  withThresholds = true;

  messageId = "abandonedKinesisStreamsTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      withThresholds: this.withThresholds,
      descriptionMessageId: "abandonedKinesisStreamsDescription",
      emptyMessageId: "noAbandonedKinesisStreams",
      dataTestIds: {
        listTestId: "sp_abandoned_kinesis_streams",
        textTestId: "p_abandoned_kinesis_streams",
        buttonTestIds: ["btn_abandoned_kinesis_streams_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_abandoned_kinesis_streams_resource",
        accessor: "cloud_resource_id"
      }),
      resourceLocation({
        headerDataTestId: "lbl_abandoned_kinesis_streams_location",
        typeAccessor: "cloud_type"
      }),
      // TODO: replace with text.js column util
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_abandoned_kinesis_streams_provisioned_shards">
            <FormattedMessage id="provisionedShards" />
          </TextWithDataTestId>
        ),
        accessor: "shardhours_capacity"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_abandoned_kinesis_streams_cost_per_hour">
            <FormattedMessage id="costPerHour" />
          </TextWithDataTestId>
        ),
        accessor: "shardhours_price",
        Cell: ({ cell: { value } }) => <FormattedMoney value={value} type={FORMATTED_MONEY_TYPES.TINY} />
      },
      detectedAt({ headerDataTestId: "lbl_abandoned_kinesis_streams_detected_at" }),
      possibleMonthlySavings({
        headerDataTestId: "lbl_abandoned_kinesis_streams_savings",
        defaultSort: "desc"
      })
    ];
  }
}

export default new AbandonedKinesisStreamsRecommendation();
