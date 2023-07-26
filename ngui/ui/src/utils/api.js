import { API } from "api/reducer";
import { reset } from "reducers/route";
import requestManager from "utils/requestManager";

/**
 *
 * @param {string} label - API label
 * @param {Object} state - Redux state
 *
 */
export const isError = (label, state) => state?.[API]?.[label]?.status?.isError;

export const rejectOnError = (dispatch, label) => () =>
  dispatch((_, getState) => (isError(label, getState()) ? Promise.reject() : Promise.resolve())).catch(() => {});

export const isTtlExpired = (timestamp) => new Date().getTime() > timestamp;

// TODO: Should reject with error to catch it in containers/services
export const checkError = (label, state) => (isError(label, state) ? Promise.reject() : Promise.resolve());

/**
 *
 * @param {object} breakdown
 * @returns {object} reformatted breakdown
 *
 * @example
 *
 * ```
 * const breakdown = {
 *   1643673600: {
 *     "1c0415ea-0d5e-43ee-82a8-234ee6706aae": {
 *       cost: 12.9804062443,
 *       name: "Ellie Byrne"
 *     }
 *   }
 * };
 *
 * const formattedBreakdown = reformatBreakdown(breakdown);
 * // const formattedBreakdown = {
 * //  1643673600: [
 * //     {
 * //       id: "1c0415ea-0d5e-43ee-82a8-234ee6706aae",
 * //       cost: 12.9804062443,
 * //       name: "Ellie Byrne"
 * //     }
 * //   ]
 * // };
 * ```
 *
 * @see https://datatrendstech.atlassian.net/wiki/spaces/OPT/pages/2727378945/Expenses+breakdown+API
 * @see https://datatrendstech.atlassian.net/wiki/spaces/OPT/pages/2686943233/Resources+count+breakdown+API
 */
export const reformatBreakdown = (breakdown) =>
  Object.fromEntries(
    Object.entries(breakdown).map(([secondsTimestamp, breakdownsData]) => {
      const breakdownsDataArray = Object.entries(breakdownsData).map(([id, body]) => ({ id, ...body }));
      return [secondsTimestamp, breakdownsDataArray];
    })
  );

export const signOut = (dispatch) => {
  dispatch(reset());
  requestManager.cancelAllPendingRequests();
};
