import localForage from "localforage";
import { combineReducers } from "redux";
import { persistReducer, createMigrate } from "redux-persist";
import { GET_TOKEN } from "api/auth/actionTypes";
import AuthReducer, { AUTH } from "api/auth/reducer";
import JiraBusReducer, { JIRA_BUS } from "api/jira_bus/reducer";
import ApiReducer, { API } from "api/reducer";
import RestapiReducer, { RESTAPI } from "api/restapi/reducer";
import ResourcesSortGroupsByReducer, {
  RESOURCES_SORT_GROUPS_BY
} from "components/CleanExpensesTableGroup/SortGroupsBySelector/reducer";
import MainMenuExpandedReducer, { MAIN_MENU_EXPANDED } from "components/CollapsableMenuDrawer/reducer";
import ExpensesBreakdownPeriodTypeReducer, {
  EXPENSES_BREAKDOWN_PERIOD_TYPE
} from "components/ExpensesBreakdown/BreakdownByPeriodWidget/reducer";
import CollapsedMenuItemsReducer, { COLLAPSED_MENU_ITEMS } from "components/MenuGroupWrapper/reducer";
import PoolsTableReducer, { EXPANDED_POOL_ROWS } from "components/PoolsTable/reducer";
import TopAlertReducer, { ALERTS } from "components/TopAlertWrapper/reducer";
import { IS_EXISTING_USER } from "components/TopAlertWrapper/TopAlertWrapper";
import { reducer as TourReducer, TOURS } from "components/Tour";
import ScopeIdReducer, { SCOPE_ID } from "containers/OrganizationSelectorContainer/reducer";
import RangeDatesReducer, { RANGE_DATES } from "containers/RangePickerFormContainer/reducer";
import RecommendationsControlsStateReducer, {
  RECOMMENDATIONS_CONTROLS_STATE
} from "containers/RecommendationsOverviewContainer/redux/controlsState/reducer";
import PinnedRecommendationsReducer, {
  PINNED_RECOMMENDATIONS
} from "containers/RecommendationsOverviewContainer/redux/pinnedRecommendations/reducer";
import { SHOW_LESS_THAN_VALUE, reducer as ShowLessThanValueReducer } from "hooks/useShowLessThanValue";
import { SHOW_WEEKENDS, reducer as ShowWeekendsReducer } from "hooks/useShowWeekends";
import migrations, { CURRENT_VERSION } from "migrations";
import CloudCostComparisonSelectedSizes, {
  CLOUD_COST_COMPARISON_SELECTED_SIZES
} from "reducers/cloudCostComparisonSelectedSizes/reducer";
import ColumnsReducer, { COLUMNS } from "reducers/columns/reducer";
import { RESET } from "reducers/route/actionTypes";
import TaskBreakdown, { TASK_BREAKDOWN } from "reducers/taskBreakdown/reducer";
import taskRunsDashboard, { TASK_RUNS_DASHBOARD } from "reducers/taskRunsDashboard/reducer";

const ROOT = "root";

const removeStorageItems = (keys) => {
  keys.forEach((key) => localForage.removeItem(key));
};

const persistConfig = {
  key: ROOT,
  storage: localForage,
  keyPrefix: "",
  blacklist: [AUTH, API, RESTAPI, JIRA_BUS, CLOUD_COST_COMPARISON_SELECTED_SIZES],
  version: CURRENT_VERSION,
  migrate: createMigrate(migrations, { debug: true })
};

const authPersistConfig = {
  key: AUTH,
  storage: localForage,
  keyPrefix: "",
  version: 1,
  whitelist: GET_TOKEN
};

const appReducer = combineReducers({
  [API]: ApiReducer,
  [AUTH]: persistReducer(authPersistConfig, AuthReducer),
  [RESTAPI]: RestapiReducer,
  [JIRA_BUS]: JiraBusReducer,
  [RESOURCES_SORT_GROUPS_BY]: ResourcesSortGroupsByReducer,
  [SCOPE_ID]: ScopeIdReducer,
  [RANGE_DATES]: RangeDatesReducer,
  [EXPANDED_POOL_ROWS]: PoolsTableReducer,
  [COLUMNS]: ColumnsReducer,
  [ALERTS]: TopAlertReducer,
  [EXPENSES_BREAKDOWN_PERIOD_TYPE]: ExpensesBreakdownPeriodTypeReducer,
  [SHOW_WEEKENDS]: ShowWeekendsReducer,
  [SHOW_LESS_THAN_VALUE]: ShowLessThanValueReducer,
  [IS_EXISTING_USER]: (state) => state || false,
  [TOURS]: TourReducer,
  [COLLAPSED_MENU_ITEMS]: CollapsedMenuItemsReducer,
  [PINNED_RECOMMENDATIONS]: PinnedRecommendationsReducer,
  [MAIN_MENU_EXPANDED]: MainMenuExpandedReducer,
  [TASK_BREAKDOWN]: TaskBreakdown,
  [CLOUD_COST_COMPARISON_SELECTED_SIZES]: CloudCostComparisonSelectedSizes,
  [RECOMMENDATIONS_CONTROLS_STATE]: RecommendationsControlsStateReducer,
  [TASK_RUNS_DASHBOARD]: taskRunsDashboard
});

const rootReducer = (incomingState, action) => {
  let state = incomingState;
  if (action.type === RESET) {
    // Remove auth to clean up a token
    removeStorageItems([AUTH]);

    // Do not persist the following keys after signing out
    const {
      [API]: api,
      [RESTAPI]: restapi,
      [JIRA_BUS]: jiraBus,
      [RANGE_DATES]: rangeDates,
      [EXPANDED_POOL_ROWS]: expandedPoolRows,
      [RECOMMENDATIONS_CONTROLS_STATE]: recommendationsControlsState,
      [COLUMNS]: columns,
      [CLOUD_COST_COMPARISON_SELECTED_SIZES]: cloudCostComparisonSelectedFlavors,
      ...rest
    } = state;

    // Recreate persistent storage with required keys
    state = {
      /* eslint-disable no-underscore-dangle */
      ...rest,
      [AUTH]: { _persist: (rest[AUTH] || {})._persist }
      /* eslint-enable no-underscore-dangle */
    };
  }

  return appReducer(state, action);
};

export default persistReducer(persistConfig, rootReducer);
