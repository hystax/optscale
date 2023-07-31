const EVENTS = Object.freeze({
  UPDATE_SEARCH_PARAMS: "updatedSearchParams"
});

export const dispatchSearchParamsChangeEvent = (params) => {
  window.dispatchEvent(new CustomEvent(EVENTS.UPDATE_SEARCH_PARAMS, { detail: { params } }));
};

export const addSearchParamsChangeListener = (listener) => window.addEventListener(EVENTS.UPDATE_SEARCH_PARAMS, listener);

export const removeSearchParamsChangeListener = (listener) => window.removeEventListener(EVENTS.UPDATE_SEARCH_PARAMS, listener);
