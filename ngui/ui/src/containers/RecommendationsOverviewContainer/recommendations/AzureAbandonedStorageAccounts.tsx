import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import AzureAbandonedStorageAccountsModal from "components/SideModalManager/SideModals/recommendations/AzureAbandonedStorageAccountsModal";
import { AZURE_STORAGE } from "hooks/useRecommendationServices";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { AZURE_CNR, FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_azure_abandoned_storage_accounts_resource",
  }),
  resourceLocation({
    headerDataTestId: "lbl_azure_abandoned_storage_accounts_location",
  }),
  {
    header: "azureAbandonedStorageAccountsCapacity",
    accessorKey: "used_capacity_gb",
    cell: ({ getValue }) => {
      const value = getValue<number | null>();
      return value == null ? "N/A" : `${value.toFixed(1)} GB`;
    },
  },
  {
    header: "azureAbandonedStorageAccountsTransactions",
    accessorKey: "transactions",
    cell: ({ getValue }) => {
      const value = getValue<number | null>();
      return value == null ? "N/A" : Math.round(value).toString();
    },
  },
  detectedAt({ headerDataTestId: "lbl_azure_abandoned_storage_accounts_detected_at" }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_azure_abandoned_storage_accounts_possible_monthly_savings",
    defaultSort: "desc",
  }),
];

class AzureAbandonedStorageAccounts extends BaseRecommendation {
  type = "azure_abandoned_storage_accounts";

  name = "azureAbandonedStorageAccounts";

  title = "azureAbandonedStorageAccountsTitle";

  descriptionMessageId = "azureAbandonedStorageAccountsDescription";

  emptyMessageId = "azureAbandonedStorageAccountsEmptyMessage";

  services = [AZURE_STORAGE];

  appliedDataSources = [AZURE_CNR];

  categories = [CATEGORY.COST];

  withExclusions = true;

  hasSettings = true;

  settingsSidemodalClass = AzureAbandonedStorageAccountsModal;

  static resourceDescriptionMessageId = "azureAbandonedStorageAccountsResourceRecommendation";

  get descriptionMessageValues() {
    const {
      idle_days_window: idleDaysWindow,
      idle_transactions_threshold: transactionsThreshold,
    } = this.options;
    return { idleDaysWindow, transactionsThreshold };
  }

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />,
      },
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />,
      },
    ]);
  }

  columns = columns;
}

export default AzureAbandonedStorageAccounts;
