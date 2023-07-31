import { applyMiddleware, compose, createStore } from "redux";
import { persistStore } from "redux-persist";
import apiMiddleware from "./middleware/api";
import rootReducer from "./reducers";

/* eslint-disable no-underscore-dangle */
const composeEnhancers =
  typeof window === "object" && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ && process.env.NODE_ENV === "development"
    ? window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__({})
    : compose;
/* eslint-enable */

const middleware =
  process.env.NODE_ENV === "development"
    ? // eslint-disable-next-line global-require
      [require("redux-immutable-state-invariant").default(), apiMiddleware]
    : [apiMiddleware];

const enhancer = composeEnhancers(applyMiddleware(...middleware));

export default (defaultStore = {}) => {
  const store = createStore(rootReducer, defaultStore, enhancer);
  const persistor = persistStore(store);
  return { store, persistor };
};
