import React from "react";
import { FormattedMessage } from "react-intl";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { AWS_S3, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, poolOwner, resource, resourceLocation } from "utils/columns";
import BaseRecommendation, { CATEGORY_SECURITY } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_s3_public_buckets"
  }),
  resourceLocation({
    headerDataTestId: "lbl_s3_public_buckets_location",
    typeAccessor: "cloud_type"
  }),
  poolOwner({
    headerDataTestId: "lbl_s3_public_buckets_pool_owner",
    id: "pool/owner"
  }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_s3_public_buckets_is_public_policy">
        <FormattedMessage id="publicPolicy" />
      </TextWithDataTestId>
    ),
    accessorKey: "is_public_policy",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return <FormattedMessage id={value ? "yes" : "no"} />;
    }
  },
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_s3_public_buckets_is_public_acls">
        <FormattedMessage id="publicAcls" />
      </TextWithDataTestId>
    ),
    accessorKey: "is_public_acls",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return <FormattedMessage id={value ? "yes" : "no"} />;
    }
  },
  detectedAt({ headerDataTestId: "lbl_s3_public_buckets_detected_at" })
];

class PublicS3Buckets extends BaseRecommendation {
  type = "s3_public_buckets";

  name = "publicS3Buckets";

  title = "publicS3BucketsTitle";

  descriptionMessageId = "publicS3BucketsDescription";

  emptyMessageId = "noPublicS3Buckets";

  services = [AWS_S3, NEBIUS_SERVICE];

  categories = [CATEGORY_SECURITY];

  withExclusions = true;

  static resourceDescriptionMessageId = "publicS3BucketsResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      { key: `${item.cloud_resource_id}-label`, value: <RecommendationListItemResourceLabel key={item.id} item={item} /> }
    ]);
  }

  columns = columns;
}

export default PublicS3Buckets;
