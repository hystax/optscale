import FormattedMoney from "components/FormattedMoney";
import { isEmptyArray } from "utils/arrays";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { ObjectValues, TODO } from "utils/types";

export const STATUS = {
  ACTIVE: "active",
  DISMISSED: "dismissed",
  EXCLUDED: "excluded",
} as const;

export const CATEGORY = {
  ALL: "all",
  COST: "cost",
  SECURITY: "security",
  CRITICAL: "critical",
  NON_EMPTY: "nonEmpty",
} as const;

export const STATUS_CATEGORY = {
  OPTIMIZATION: "optimizations",
  DISMISSED_OPTIMIZATION: "dismissed_optimizations",
  EXCLUDED_OPTIMIZATION: "excluded_optimizations",
} as const;

const statusToCategoryMap: Record<Status, StatusCategory> = {
  [STATUS.ACTIVE]: STATUS_CATEGORY.OPTIMIZATION,
  [STATUS.DISMISSED]: STATUS_CATEGORY.DISMISSED_OPTIMIZATION,
  [STATUS.EXCLUDED]: STATUS_CATEGORY.EXCLUDED_OPTIMIZATION,
};

export const RECOMMENDATION_COLOR = Object.freeze({
  SUCCESS: "success",
  WARNING: "warning",
  ERROR: "error",
});

type Status = ObjectValues<typeof STATUS>;
type Category = ObjectValues<typeof CATEGORY>;
type StatusCategory = ObjectValues<typeof STATUS_CATEGORY>;

class BaseRecommendation {
  // todo: make type/name/title static
  type = "optimization_type";

  name = "optimizationName";

  title = "optimizationNameTitle";

  categories: Category[] = [CATEGORY.COST];

  apiResponse: TODO;
  status: Status;
  statusCategory: string;

  constructor(status: Status, apiResponse: TODO) {
    this.initialize(status, apiResponse);
  }

  initialize(status: Status, apiResponse: TODO = {}) {
    this.apiResponse = apiResponse;
    this.status = status;
    this.statusCategory = statusToCategoryMap[status];
  }

  get isActive() {
    return this.status === STATUS.ACTIVE;
  }

  get isDismissed() {
    return this.status === STATUS.DISMISSED;
  }

  get isExcluded() {
    return this.status === STATUS.EXCLUDED;
  }

  get recommendation() {
    return this.apiResponse[this.statusCategory]?.[this.type] ?? {};
  }

  get error() {
    return this.apiResponse[this.statusCategory]?.[this.type]?.error;
  }

  get hasError() {
    return !!this.error;
  }

  get items() {
    return this.recommendation.items || [];
  }

  get allDataSources() {
    return this.apiResponse[this.statusCategory]?.[this.type]?.cloud_accounts ?? [];
  }

  get options() {
    return this.recommendation.options || {};
  }

  // Organization options come from a different API endpoint. They are independent at this point.
  get organizationOptions() {
    return this.apiResponse?.organizationOptions?.[this.type] || {};
  }

  get optionsInSync() {
    const { organizationOptions: { isUpdated = false } = {} } = this;

    return !isUpdated;
  }

  get count() {
    return this.recommendation.count || 0;
  }

  // TODO: see label() and value() - saving can be 0, but can not be present in the response. Need a generic solution.
  get saving() {
    return this.recommendation.saving || 0;
  }

  get hasSaving() {
    return Object.hasOwn(this.recommendation, "saving");
  }

  get value() {
    return this.hasSaving ? <FormattedMoney type={FORMATTED_MONEY_TYPES.COMPACT} value={this.saving} /> : this.count;
  }

  // TODO: there is no connection between the category and the label.
  // If it is "cost", we should display "savings", should not rely on the actual API response
  get label() {
    return this.hasSaving ? "savings" : "count";
  }

  get hasItems() {
    return !isEmptyArray(this.items);
  }

  hasCategory(category: Category) {
    return this.categories.includes(category);
  }

  // this will be overridden for each recommendation
  get color() {
    if (this.saving === 0 && this.count === 0) {
      return RECOMMENDATION_COLOR.SUCCESS;
    }

    if (this.saving === 0 && this.count !== 0) {
      return RECOMMENDATION_COLOR.WARNING;
    }

    if (this.saving > 100) {
      return RECOMMENDATION_COLOR.ERROR;
    }

    return undefined;
  }

  get previewItems() {
    return this.items;
  }

  dismissible = true;

  columns: TODO[] = [];

  descriptionMessageId = "my_message";

  emptyMessageId = "noItems";

  services: string[] = [];

  appliedDataSources: string[] = [];

  sampleValues = {};

  withCleanupScripts = false;

  static getResourceDescriptionMessageValues() {}

  get descriptionMessageValues() {
    return this.sampleValues;
  }

  set descriptionMessageValues(v) {
    this.sampleValues = v;
  }
}

export default BaseRecommendation;
