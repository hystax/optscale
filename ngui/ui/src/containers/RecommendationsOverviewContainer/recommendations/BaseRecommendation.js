import React from "react";
import FormattedMoney from "components/FormattedMoney";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { FORMATTED_MONEY_TYPES } from "utils/constants";

export const ACTIVE = "active";
export const DISMISSED = "dismissed";
export const EXCLUDED = "excluded";

export const CATEGORY_ALL = "all";
export const CATEGORY_COST = "cost";
export const CATEGORY_SECURITY = "security";
export const CATEGORY_CRITICAL = "critical";
export const CATEGORY_NON_EMPTY = "nonEmpty";

export const RECOMMENDATION_COLOR = Object.freeze({
  SUCCESS: "success",
  WARNING: "warning",
  ERROR: "error"
});

class BaseRecommendation {
  // todo: make type/name/title static
  type = "optimization_type";

  name = "optimizationName";

  title = "optimizationNameTitle";

  categories = [CATEGORY_COST];

  constructor(status, apiResponse) {
    this.initialize(status, apiResponse);
  }

  initialize(status, apiResponse = {}) {
    this.apiResponse = apiResponse;
    this.status = status;
    this.statusCategory = {
      [ACTIVE]: "optimizations",
      [DISMISSED]: "dismissed_optimizations",
      [EXCLUDED]: "excluded_optimizations"
    }[status];
  }

  get isActive() {
    return this.status === ACTIVE;
  }

  get isDismissed() {
    return this.status === DISMISSED;
  }

  get isExcluded() {
    return this.status === EXCLUDED;
  }

  get recommendation() {
    return this.apiResponse[this.statusCategory]?.[this.type] || {};
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
  // If it is "cost", we shoud display "savings", should not rely on the actual API response
  get label() {
    return this.hasSaving ? "savings" : "count";
  }

  get hasItems() {
    return !isEmptyArray(this.items);
  }

  hasCategory(category) {
    return this.categories.includes(category);
  }

  // this will be overriden for each recommendation
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

  dismissable = true;

  columns = [];

  descriptionMessageId = "my_message";

  emptyMessageId = "noItems";

  services = [];

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
