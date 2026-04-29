import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import AzureColdTierCandidatesModal from "components/SideModalManager/SideModals/recommendations/AzureColdTierCandidatesModal";
import TextWithDataTestId from "components/TextWithDataTestId";
import { AZURE_STORAGE } from "hooks/useRecommendationServices";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { AZURE_CNR, FORMATTED_MONEY_TYPES } from "utils/constants";
import { TODO } from "utils/types";
import BaseRecommendation, { CATEGORY } from "./BaseRecommendation";

const tierMoveCell = ({ row }: { row: { original: TODO } }) => {
  const current = row.original?.current_tier ?? "";
  const target = row.original?.target_tier ?? "";
  return `${current} → ${target}`;
};

const savingCell = ({ row }: { row: { original: TODO } }) => {
  const item = row.original;
  const breakdown = item?.saving_breakdown ?? {};
  const reservationApplied = item?.reservation_applied === true;
  return (
    <span>
      <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item?.saving} />
      {reservationApplied ? (
        <span style={{ marginLeft: 4, fontSize: "0.75em", opacity: 0.7 }}>
          (PAYG <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={breakdown?.payg} />
          {" / eff "}
          <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={breakdown?.effective} />
          )
        </span>
      ) : null}
    </span>
  );
};

const columns = [
  resource({
    headerDataTestId: "azure_cold_tier_resource",
  }),
  resourceLocation({
    headerDataTestId: "azure_cold_tier_location",
    typeAccessor: "cloud_type",
  }),
  {
    header: (
      <TextWithDataTestId dataTestId="azure_cold_tier_move">
        <FormattedMessage id="azureColdTierCandidatesTierMove" />
      </TextWithDataTestId>
    ),
    accessorKey: "target_tier",
    cell: tierMoveCell,
  },
  {
    header: (
      <TextWithDataTestId dataTestId="azure_cold_tier_gb">
        <FormattedMessage id="azureColdTierCandidatesGb" />
      </TextWithDataTestId>
    ),
    accessorKey: "gb",
  },
  {
    header: (
      <TextWithDataTestId dataTestId="azure_cold_tier_confidence">
        <FormattedMessage id="azureColdTierCandidatesConfidence" />
      </TextWithDataTestId>
    ),
    accessorKey: "confidence",
    cell: ({ cell }: { cell: { getValue: () => string } }) => {
      const value = cell.getValue();
      return <FormattedMessage id={`confidence.${value}`} defaultMessage={value} />;
    },
  },
  {
    header: (
      <TextWithDataTestId dataTestId="azure_cold_tier_signal">
        <FormattedMessage id="azureColdTierCandidatesSignal" />
      </TextWithDataTestId>
    ),
    accessorKey: "signal_used",
  },
  detectedAt({ headerDataTestId: "azure_cold_tier_detected_at" }),
  {
    header: (
      <TextWithDataTestId dataTestId="azure_cold_tier_savings">
        <FormattedMessage id="possibleMonthlySavings" />
      </TextWithDataTestId>
    ),
    accessorKey: "saving",
    cell: savingCell,
    ...possibleMonthlySavings({
      headerDataTestId: "azure_cold_tier_savings",
      defaultSort: "desc",
    }),
  },
];

class AzureColdTierCandidates extends BaseRecommendation {
  type = "azure_cold_tier_candidates";

  name = "azureColdTierCandidates";

  title = "azureColdTierCandidatesTitle";

  descriptionMessageId = "azureColdTierCandidatesDescription";

  emptyMessageId = "azureColdTierCandidatesEmptyMessage";

  appliedDataSources = [AZURE_CNR];

  services = [AZURE_STORAGE];

  categories = [CATEGORY.COST];

  withExclusions = true;

  hasSettings = true;

  settingsSidemodalClass = AzureColdTierCandidatesModal;

  static resourceDescriptionMessageId = "azureColdTierCandidatesResourceRecommendation";

  get previewItems() {
    return this.items.map((item: TODO) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel key={item.id} item={item} />,
      },
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />,
      },
    ]);
  }

  columns = columns as never[];
}

export default AzureColdTierCandidates;
