import React from "react";
import FormattedMoney from "components/FormattedMoney";
import HeaderHelperCell from "components/HeaderHelperCell";
import { detectedAt, resource, resourceLocation, size } from "utils/columns";
import { FORMATTED_MONEY_TYPES, RECOMMENDATION_RESERVED_INSTANCES, RESERVED_INSTANCES_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class ReservedInstancesRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_RESERVED_INSTANCES;

  moduleName = RESERVED_INSTANCES_TYPE;

  withExclusions = true;

  messageId = "reservedInstancesSavingOpportunitiesTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      descriptionMessageId: "reservedInstancesDescription",
      emptyMessageId: "noReservedInstances",
      dataTestIds: {
        listTestId: "sp_reserved_instances",
        textTestId: "p_reserved_instances",
        buttonTestIds: ["btn_ri_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_ri_resource"
      }),
      resourceLocation({
        headerDataTestId: "lbl_ri_location"
      }),
      size({
        headerDataTestId: "lbl_ri_size"
      }),
      detectedAt({ headerDataTestId: "lbl_ri_detected_at" }),
      {
        header: (
          <HeaderHelperCell
            titleDataTestId="lbl_ri_savings_min"
            titleMessageId="savingsWithMinimalCommitment"
            helperMessageId="savingsWithMinimalCommitmentHelp"
          />
        ),
        accessorKey: "saving",
        defaultSort: "desc",
        cell: ({ cell }) => {
          const value = cell.getValue();

          return <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />;
        }
      },
      {
        header: (
          <HeaderHelperCell
            titleDataTestId="lbl_ri_savings_avg"
            titleMessageId="savingsWithAverageCommitment"
            helperMessageId="savingsWithAverageCommitmentHelp"
          />
        ),
        accessorKey: "average_saving",
        cell: ({ cell }) => {
          const value = cell.getValue();

          return <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />;
        }
      }
    ];
  }
}

export default new ReservedInstancesRecommendation();
