import { SAVE_HIDDEN_COLUMNS } from "./actionTypes";

export const RAW_EXPENSES = "rawExpensesTable";
export const ENVIRONMENTS_TABLE = "environmentsTable";
export const COLUMNS = "columns";

const reducer = (state = {}, action) => {
  switch (action.type) {
    case SAVE_HIDDEN_COLUMNS: {
      const { tableUID, hiddenColumnsArray } = action.payload;
      return {
        ...state,
        [tableUID]: hiddenColumnsArray
      };
    }
    default:
      return state;
  }
};

export default reducer;
