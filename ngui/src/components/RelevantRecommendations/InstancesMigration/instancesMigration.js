import React from "react";
import { FormattedMessage } from "react-intl";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabelGrid from "components/IconLabelGrid";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation, size } from "utils/columns";
import { RECOMMENDATION_INSTANCE_MIGRATION, INSTANCE_MIGRATION_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class InstancesMigrationRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_INSTANCE_MIGRATION;

  moduleName = INSTANCE_MIGRATION_TYPE;

  withExclusions = true;

  messageId = "instanceMigrationTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      descriptionMessageId: "instanceMigrationDescription",
      emptyMessageId: "noInstanceMigrations",
      dataTestIds: {
        listTestId: "sp_instances_migration",
        textTestId: "p_instances_migration",
        buttonTestIds: ["btn_im_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_im_resource"
      }),
      resourceLocation({
        headerDataTestId: "lbl_im_location",
        regionAccessor: "current_region"
      }),
      size({
        headerDataTestId: "lbl_im_size"
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_im_recomm_region">
            <FormattedMessage id="recommendedRegion" />
          </TextWithDataTestId>
        ),
        accessorKey: "recommended_region",
        cell: ({ row: { original } }) => (
          <IconLabelGrid
            label={original.recommended_region}
            startIcon={<CloudTypeIcon fontSize="small" type={original.cloud_type} />}
          />
        )
      },
      detectedAt({ headerDataTestId: "lbl_im_detected_at" }),
      possibleMonthlySavings({
        headerDataTestId: "lbl_im_possible_monthly_savings",
        defaultSort: "desc"
      })
    ];
  }
}

export default new InstancesMigrationRecommendation();
