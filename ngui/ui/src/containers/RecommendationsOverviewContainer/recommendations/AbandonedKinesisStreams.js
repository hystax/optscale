import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import AbandonedKinesisStreamsModal from "components/SideModalManager/SideModals/recommendations/AbandonedKinesisStreamsModal";
import TextWithDataTestId from "components/TextWithDataTestId";
import { AWS_KINESIS } from "hooks/useRecommendationServices";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_abandoned_kinesis_streams_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_abandoned_kinesis_streams_location",
    typeAccessor: "cloud_type"
  }),
  // TODO: replace with text.js column util
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_abandoned_kinesis_streams_provisioned_shards">
        <FormattedMessage id="provisionedShards" />
      </TextWithDataTestId>
    ),
    accessorKey: "shardhours_capacity"
  },
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_abandoned_kinesis_streams_cost_per_hour">
        <FormattedMessage id="costPerHour" />
      </TextWithDataTestId>
    ),
    accessorKey: "shardhours_price",
    cell: ({ cell }) => <FormattedMoney value={cell.getValue()} type={FORMATTED_MONEY_TYPES.TINY} />
  },
  detectedAt({ headerDataTestId: "lbl_abandoned_kinesis_streams_detected_at" }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_abandoned_kinesis_streams_savings",
    defaultSort: "desc"
  })
];

class AbandonedKinesisStreams extends BaseRecommendation {
  type = "abandoned_kinesis_streams";

  name = "abandonedKinesisStreams";

  title = "abandonedKinesisStreamsTitle";

  descriptionMessageId = "abandonedKinesisStreamsDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;

    return { daysThreshold };
  }

  emptyMessageId = "noAbandonedKinesisStreams";

  services = [AWS_KINESIS];

  categories = [CATEGORY_COST];

  hasSettings = true;

  settingsSidemodalClass = AbandonedKinesisStreamsModal;

  withExclusions = true;

  static resourceDescriptionMessageId = "abandonedKinesisStreamsResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />
      }
    ]);
  }

  columns = columns;
}

export default AbandonedKinesisStreams;
