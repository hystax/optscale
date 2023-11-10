import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import HeaderHelperCell from "components/HeaderHelperCell";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import AbandonedS3BucketsModal from "components/SideModalManager/SideModals/recommendations/AbandonedS3BucketsModal";
import TextWithDataTestId from "components/TextWithDataTestId";
import { AWS_S3, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, poolOwner, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import averageDataSize from "utils/columns/averageDataSize";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_s3_abandoned_buckets_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_s3_abandoned_buckets_location",
    typeAccessor: "cloud_type"
  }),
  poolOwner({
    headerDataTestId: "lbl_s3_abandoned_buckets_pool_owner",
    id: "pool/owner"
  }),
  averageDataSize({
    headerDataTestId: "lbl_s3_abandoned_buckets_avg_data_size",
    accessorKey: "avg_data_size"
  }),
  {
    header: (
      <HeaderHelperCell
        titleDataTestId="lbl_s3_abandoned_buckets_tier1_requests"
        titleMessageId="tier1Requests"
        helperMessageId="tier1S3BucketRequestHelp"
      />
    ),
    accessorKey: "tier_1_request_quantity"
  },
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_s3_abandoned_buckets_get_requests">
        <FormattedMessage id="getRequests" />
      </TextWithDataTestId>
    ),
    accessorKey: "tier_2_request_quantity"
  },
  detectedAt({ headerDataTestId: "lbl_s3_abandoned_buckets_detected_at" }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_s3_abandoned_buckets_savings",
    defaultSort: "desc"
  })
];

class AbandonedS3Buckets extends BaseRecommendation {
  type = "s3_abandoned_buckets";

  name = "abandonedS3Buckets";

  title = "abandonedS3Buckets";

  descriptionMessageId = "abandonedS3BucketsDescription";

  get descriptionMessageValues() {
    const {
      days_threshold: daysThreshold,
      data_size_threshold: dataSizeAvg,
      tier_1_request_quantity_threshold: tier1RequestsQuantity,
      tier_2_request_quantity_threshold: tier2RequestsQuantity
    } = this.options;

    return { daysThreshold, dataSizeAvg, tier1RequestsQuantity, tier2RequestsQuantity };
  }

  emptyMessageId = "noAbandonedS3Buckets";

  services = [AWS_S3, NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  hasSettings = true;

  settingsSidemodalClass = AbandonedS3BucketsModal;

  withExclusions = true;

  static resourceDescriptionMessageId = "abandonedS3BucketsResourceRecommendation";

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

export default AbandonedS3Buckets;
