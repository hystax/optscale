import { TAG_BE_FILTER, WITHOUT_TAG_BE_FILTER } from "utils/constants";
import DataSourceFilter from "./DataSourceFilter";
import GoalsFilter from "./GoalsFilter";
import K8sNamespaceFilter from "./K8sNamespaceFilter";
import K8sNodeFilter from "./K8sNodeFilter";
import K8sServiceFilter from "./K8sServiceFilter";
import NetworkTrafficFromFilter from "./NetworkTrafficFromFilter";
import NetworkTrafficToFilter from "./NetworkTrafficToFilter";
import OwnerFilter from "./OwnerFilter";
import PoolFilter from "./PoolFilter";
import RegionFilter from "./RegionFilter";
import ResourceStateFilter from "./ResourceStateFilter";
import ResourceTypeFilter from "./ResourceTypeFilter";
import ServiceFilter from "./ServiceType";
import StatusFilter from "./StatusFilter";
import TagFilter from "./TagFilter";
import WithAvailableSavingsFilter from "./WithAvailableSavingsFilter";
import WithoutTagFilter from "./WithoutTagFilter";
import WithViolatedConstraintsFilter from "./WithViolatedConstraintsFilter";

export const ALL_CATEGORY = "all";
export const COST_CATEGORY = "cost";
export const PERFORMANCE_CATEGORY = "performance";
export const SECURITY_CATEGORY = "security";

export const CATEGORIES = Object.freeze({
  [ALL_CATEGORY]: "all",
  [COST_CATEGORY]: "costOptimization",
  [SECURITY_CATEGORY]: "security"
});

export const SUPPORTED_CATEGORIES = Object.freeze(Object.keys(CATEGORIES));

export const TAGS_RELATED_FILTERS = [TAG_BE_FILTER, WITHOUT_TAG_BE_FILTER];

export const RESOURCE_FILTERS = [
  DataSourceFilter,
  PoolFilter,
  OwnerFilter,
  RegionFilter,
  ServiceFilter,
  ResourceTypeFilter,
  ResourceStateFilter,
  WithAvailableSavingsFilter,
  WithViolatedConstraintsFilter,
  K8sNodeFilter,
  K8sNamespaceFilter,
  K8sServiceFilter,
  TagFilter,
  WithoutTagFilter,
  NetworkTrafficFromFilter,
  NetworkTrafficToFilter
];

export const RESOURCE_FILTERS_NAMES = RESOURCE_FILTERS.map((ResourceFilter) => ResourceFilter.filterName);

export const RESOURCE_FILTERS_API_NAMES = RESOURCE_FILTERS.map((ResourceFilter) => ResourceFilter.apiName);

export const ML_MODELS_FILTERS = [OwnerFilter, StatusFilter, GoalsFilter];
export const ML_RUNS_FILTERS = [StatusFilter, GoalsFilter];
export const ML_MODEL_RUNS_FILTERS = [StatusFilter, GoalsFilter];

export const ML_MODELS_FILTERS_NAMES = ML_MODELS_FILTERS.map((ResourceFilter) => ResourceFilter.filterName);
export const ML_RUNS_FILTERS_NAMES = ML_RUNS_FILTERS.map((ResourceFilter) => ResourceFilter.filterName);
