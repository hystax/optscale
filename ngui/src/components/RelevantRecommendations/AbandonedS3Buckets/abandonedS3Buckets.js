import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import HeaderHelperCell from "components/HeaderHelperCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, poolOwner, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { RECOMMENDATION_ABANDONED_S3_BUCKETS, ABANDONED_S3_BUCKETS_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class AbandonedS3BucketsRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_ABANDONED_S3_BUCKETS;

  moduleName = ABANDONED_S3_BUCKETS_TYPE;

  messageId = "abandonedS3Buckets";

  withExclusions = true;

  withThresholds = true;

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      withThresholds: this.withThresholds,
      descriptionMessageId: "abandonedS3BucketsDescription",
      emptyMessageId: "noAbandonedS3Buckets",
      dataTestIds: {
        listTestId: "sp_abandoned_s3_buckets",
        textTestId: "p_abandoned_s3_buckets",
        buttonTestIds: ["btn_abandoned_s3_buckets_download"]
      }
    };
  }

  static configureColumns() {
    return [
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
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_s3_abandoned_buckets_avg_data_size">
            <FormattedMessage id="dataSizeAvg" />
          </TextWithDataTestId>
        ),
        accessorKey: "avg_data_size",
        cell: ({ cell }) => (
          <>
            <FormattedNumber value={cell.getValue()} maximumFractionDigits={2} />
            &nbsp;
            <FormattedMessage id="digitalUnits" values={{ unit: "megabyte" }} />
          </>
        )
      },
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
  }
}

export default new AbandonedS3BucketsRecommendation();
