import configureStore from "store";
import { mockStore, MockState } from "utils/mockStore";

const stateData = { someData: "" };

describe("getState() should return a valid object", () => {
  test("MockState object as a parameters", () => {
    const store = mockStore(new MockState(stateData));
    const { store: expectedStore } = configureStore(new MockState(stateData));
    expect(store.getState()).toEqual(expectedStore.getState());
  });
  test("{ state: ...} } as a parameters", () => {
    const store = mockStore({ state: stateData });
    const { store: expectedStore } = configureStore({ state: stateData });
    expect(store.getState()).toEqual(expectedStore.getState());
  });
});
