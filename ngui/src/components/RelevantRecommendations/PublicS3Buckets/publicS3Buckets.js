import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, poolOwner, resource, resourceLocation } from "utils/columns";
import { RECOMMENDATION_PUBLIC_S3_BUCKETS, PUBLIC_S3_BUCKETS_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class PublicS3BucketsRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_PUBLIC_S3_BUCKETS;

  moduleName = PUBLIC_S3_BUCKETS_TYPE;

  withExclusions = true;

  messageId = "publicS3BucketsTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      descriptionMessageId: "publicS3BucketsDescription",
      emptyMessageId: "noPublicS3Buckets",
      dataTestIds: {
        listTestId: "sp_s3_public_buckets",
        textTestId: "p_s3_public_buckets",
        buttonTestIds: ["btn_s3_public_buckets_download"]
      }
    };
  }

  static configureColumns() {
    return [
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
  }
}

export default new PublicS3BucketsRecommendation();
