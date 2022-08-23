import localForage from "localforage";
import { combineReducers } from "redux";
import { persistReducer, createMigrate } from "redux-persist";
import { GET_TOKEN } from "api/auth/actionTypes";
import AuthReducer, { AUTH } from "api/auth/reducer";
import JiraBusReducer, { JIRA_BUS } from "api/jira_bus/reducer";
import KeeperReducer, { KEEPER } from "api/keeper/reducer";
import ApiReducer, { API } from "api/reducer";
import RestapiReducer, { RESTAPI } from "api/restapi/reducer";
import SlackerReducer, { SLACKER } from "api/slacker/reducer";
import ResourcesSortGroupsByReducer, {
  RESOURCES_SORT_GROUPS_BY
} from "components/CleanExpensesTableGroup/SortGroupsBySelector/reducer";
import CloudHealthReducer, { CLOUD_HEALTH } from "components/CloudHealth/reducer";
import ExpensesBreakdownPeriodTypeReducer, {
  EXPENSES_BREAKDOWN_PERIOD_TYPE
} from "components/ExpensesBreakdown/BreakdownByPeriodWidget/reducer";
import CollapsedMenuItemsReducer, { COLLAPSED_MENU_ITEMS } from "components/MenuGroupWrapper/reducer";
import PoolsTableReducer, { EXPANDED_POOL_ROWS } from "components/PoolsTable/reducer";
import { reducer as ProductTourReducer, TOURS } from "components/ProductTour";
import TopAlertReducer, { ALERTS } from "components/TopAlertWrapper/reducer";
import ScopeIdReducer, { SCOPE_ID } from "containers/OrganizationSelectorContainer/reducer";
import RangeDatesReducer, { RANGE_DATES } from "containers/RangePickerFormContainer/reducer";
import { SHOW_EXPENSES_DAILY_BREAKDOWN, reducer as ShowExpensesBreakdownReducer } from "hooks/useShowExpensesDailyBreakdown";
import { SHOW_LESS_THAN_VALUE, reducer as ShowLessThanValueReducer } from "hooks/useShowLessThanValue";
import { SHOW_WEEKENDS, reducer as ShowWeekendsReducer } from "hooks/useShowWeekends";
import migrations, { CURRENT_VERSION } from "migrations";
import ColumnsReducer, { COLUMNS } from "reducers/columns/reducer";
import ResourcesReducers, { RESOURCES } from "reducers/resources/reducer";
import { RESET } from "reducers/route/actionTypes";

const ROOT = "root";

const removeStorageItems = (keys) => {
  keys.forEach((key) => localForage.removeItem(key));
};

const removeLegacyStorageItems = (keys) => {
  keys.forEach((key) => localStorage.removeItem(key));
};

const persistConfig = {
  key: ROOT,
  storage: localForage,
  keyPrefix: "",
  blacklist: [API, AUTH, KEEPER, RESTAPI],
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
  [KEEPER]: KeeperReducer,
  [RESTAPI]: RestapiReducer,
  [SLACKER]: SlackerReducer,
  [JIRA_BUS]: JiraBusReducer,
  [CLOUD_HEALTH]: CloudHealthReducer,
  [RESOURCES_SORT_GROUPS_BY]: ResourcesSortGroupsByReducer,
  [RESOURCES]: ResourcesReducers,
  [SCOPE_ID]: ScopeIdReducer,
  [RANGE_DATES]: RangeDatesReducer,
  [EXPANDED_POOL_ROWS]: PoolsTableReducer,
  [COLUMNS]: ColumnsReducer,
  [ALERTS]: TopAlertReducer,
  [EXPENSES_BREAKDOWN_PERIOD_TYPE]: ExpensesBreakdownPeriodTypeReducer,
  [SHOW_WEEKENDS]: ShowWeekendsReducer,
  [SHOW_LESS_THAN_VALUE]: ShowLessThanValueReducer,
  [TOURS]: ProductTourReducer,
  [SHOW_EXPENSES_DAILY_BREAKDOWN]: ShowExpensesBreakdownReducer,
  [COLLAPSED_MENU_ITEMS]: CollapsedMenuItemsReducer
});

const rootReducer = (incomingState, action) => {
  let state = incomingState;
  if (action.type === RESET) {
    // Remove auth to clean up a token
    removeStorageItems([AUTH]);
    // Remove from local storage. This is temporary, we stopped persisting them, but the data will remain in the local storage in users' browsers.
    // Will be able to remove later, not earlier than token expiration, probably in a few weeks for safety
    // Date added March 29th 2021
    removeLegacyStorageItems([RESTAPI, KEEPER, AUTH, ROOT]);
    removeLegacyStorageItems([`persist:${RESTAPI}`, `persist:${KEEPER}`]);

    // Do not persist the following keys after signing out
    const {
      [API]: api,
      [RANGE_DATES]: rangeDates,
      [EXPANDED_POOL_ROWS]: expandedPoolRows,
      [COLUMNS]: columns,
      [CLOUD_HEALTH]: cloudHealth,
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
