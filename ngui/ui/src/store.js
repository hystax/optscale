import { applyMiddleware, compose, createStore } from "redux";
import { persistStore } from "redux-persist";
import apiMiddleware from "./middleware/api";
import rootReducer from "./reducers";

/* eslint-disable no-underscore-dangle */
const composeEnhancers =
  typeof window === "object" && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ && import.meta.env.DEV
    ? window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__({})
    : compose;
/* eslint-enable */

const middleware = import.meta.env.DEV
  ? [(await import("redux-immutable-state-invariant")).default(), apiMiddleware]
  : [apiMiddleware];

const enhancer = composeEnhancers(applyMiddleware(...middleware));

export default (defaultStore = {}) => {
  const store = createStore(rootReducer, defaultStore, enhancer);
  const persistor = persistStore(store);
  return { store, persistor };
};
