import configureStore from "store";

/**
 *
 * @param {object | MockState} mockState - object or instance of the MockState object
 * @returns configured store
 */
export const mockStore = (mockState) => {
  const { store } = configureStore(mockState.state);
  return store;
};
