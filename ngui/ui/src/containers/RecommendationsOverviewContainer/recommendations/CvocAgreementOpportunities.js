import React from "react";
import FormattedMoney from "components/FormattedMoney";
import HeaderHelperCell from "components/HeaderHelperCell";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import CvocAgreementOpportunitiesModal from "components/SideModalManager/SideModals/recommendations/CvocAgreementOpportunitiesModal";
import { NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, resource, resourceLocation, size } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_cvos_agreement_opportunities_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_cvos_agreement_opportunities_location"
  }),
  size({
    headerDataTestId: "lbl_cvos_agreement_opportunities_size"
  }),
  detectedAt({ headerDataTestId: "lbl_cvos_agreement_opportunities_detected_at" }),
  {
    header: (
      <HeaderHelperCell
        titleDataTestId="lbl_ri_savings_min"
        titleMessageId="savingWithSixMonthsReservationOffer"
        helperMessageId="cvosSavingsWithSixMonthCommitmentHelp"
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
        titleDataTestId="lbl_cvos_agreement_opportunities_savings_avg"
        titleMessageId="savingWithTwelveMonthsReservationOffer"
        helperMessageId="cvosSavingsWithAverageCommitmentHelp"
      />
    ),
    accessorKey: "saving_1_year",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />;
    }
  }
];

class CvocAgreementOpportunities extends BaseRecommendation {
  type = "cvos_opportunities";

  name = "cvosAgreementOpportunities";

  title = "cvosAgreementOpportunitiesTitle";

  descriptionMessageId = "cvosAgreementOpportunitiesDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;

    return { daysThreshold };
  }

  emptyMessageId = "noCvosAgreementOpportunities";

  services = [NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  hasSettings = true;

  settingsSidemodalClass = CvocAgreementOpportunitiesModal;

  withExclusions = true;

  static resourceDescriptionMessageId = "abandonedImagesResourceRecommendation";

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

export default CvocAgreementOpportunities;
