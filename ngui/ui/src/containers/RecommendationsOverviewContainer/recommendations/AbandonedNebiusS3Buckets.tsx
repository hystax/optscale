import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import AbandonedNebiusS3BucketsModal from "components/SideModalManager/SideModals/recommendations/AbandonedNebiusS3BucketsModal";
import { NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, poolOwner, possibleMonthlySavings, resource, resourceLocation, text } from "utils/columns";
import averageDataSize from "utils/columns/averageDataSize";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_location",
    typeAccessor: "cloud_type"
  }),
  poolOwner({
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_pool_owner",
    id: "pool/owner"
  }),
  averageDataSize({
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_avg_data_size",
    accessorKey: "avg_data_size"
  }),
  text({
    headerMessageId: "getRequests",
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_get_requests",
    accessorKey: "get_request_quantity"
  }),
  text({
    headerMessageId: "postRequests",
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_post_requests",
    accessorKey: "post_request_quantity"
  }),
  text({
    headerMessageId: "putRequests",
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_put_requests",
    accessorKey: "put_request_quantity"
  }),
  text({
    headerMessageId: "headRequests",
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_head_requests",
    accessorKey: "head_request_quantity"
  }),
  text({
    headerMessageId: "optionsRequests",
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_options_requests",
    accessorKey: "options_request_quantity"
  }),
  text({
    headerMessageId: "deleteRequests",
    headerDataTestId: "lbl_nebius_s3_abandoned_buckets_delete_requests",
    accessorKey: "delete_request_quantity"
  }),
  detectedAt({ headerDataTestId: "lbl_nebius_s3_abandoned_buckets_detected_at" }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_s3_abandoned_buckets_savings",
    defaultSort: "desc"
  })
];

class AbandonedNebiusS3Buckets extends BaseRecommendation {
  type = "s3_abandoned_buckets_nebius";

  name = "abandonedNebiusS3Buckets";

  title = "abandonedNebiusS3Buckets";

  descriptionMessageId = "abandonedNebiusS3BucketsDescription";

  // TODO: for all recommendations, description message values and options form values looks like they could be merged
  get descriptionMessageValues() {
    const {
      days_threshold: daysThreshold,
      data_size_threshold: dataSizeAvg,
      get_request_quantity_threshold: getRequestsQuantity,
      post_request_quantity_threshold: postRequestsQuantity,
      put_request_quantity_threshold: putRequestsQuantity,
      head_request_quantity_threshold: headRequestsQuantity,
      options_request_quantity_threshold: optionsRequestsQuantity,
      delete_request_quantity_threshold: deleteRequestsQuantity
    } = this.options;

    return {
      dataSizeAvg,
      daysThreshold,
      getRequestsQuantity,
      postRequestsQuantity,
      putRequestsQuantity,
      headRequestsQuantity,
      optionsRequestsQuantity,
      deleteRequestsQuantity
    };
  }

  emptyMessageId = "noAbandonedNebiusS3Buckets";

  services = [NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  hasSettings = true;

  settingsSidemodalClass = AbandonedNebiusS3BucketsModal;

  withExclusions = true;

  static resourceDescriptionMessageId = "abandonedNebiusS3BucketsResourceRecommendation";

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

export default AbandonedNebiusS3Buckets;
