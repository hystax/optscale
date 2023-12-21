import configureStore from "store";
import { MockState } from "utils/MockState";
import { mockStore } from "utils/mockStore";

const stateData = { someData: "" };

describe("getState() should return a valid object", () => {
  test("MockState object as a parameters", () => {
    const store = mockStore(MockState(stateData));
    const { store: expectedStore } = configureStore(MockState(stateData));
    expect(store.getState()).toEqual(expectedStore.getState());
  });
  test("{ state: ...} } as a parameters", () => {
    const store = mockStore({ state: stateData });
    const { store: expectedStore } = configureStore({ state: stateData });
    expect(store.getState()).toEqual(expectedStore.getState());
  });
});
