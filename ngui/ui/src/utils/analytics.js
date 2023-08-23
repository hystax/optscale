import googleAnalytics from "@analytics/google-analytics";
import Analytics from "analytics";
import { isDemo, isProduction } from "urls";
import { initialize } from "utils/hotjar";
import { getEnvironmentVariable } from "./env";
import { isEmpty } from "./objects";

// Hotjar analytics
const isEligibleEnvironment = () => isProduction() || isDemo();
export const initializeHotjar = () => isEligibleEnvironment() && initialize(getEnvironmentVariable("REACT_APP_HOTJAR_ID"));

// Google analytics
let identificationLoading = false;
let resetLoading = false;

const qaDebugGa = localStorage.getItem("qaDebugGa");

const analyticsStyle = "color:blue;";
const log = (msg, ...args) => {
  if (qaDebugGa) {
    console.log(msg, analyticsStyle, ...args);
  }
};

const groupLog = (header, messages) => {
  if (qaDebugGa) {
    console.group(`%c${header}`, analyticsStyle);
    messages.forEach((m) => console.log(...m));
    console.groupEnd();
  }
};

export const GA_EVENT_CATEGORIES = Object.freeze({
  DATA_SOURCE: "Data Source",
  USER: "User",
  LIVE_DEMO: "Live Demo",
  ENVIRONMENT: "Environment"
});

log(`%cGA inited with ${getEnvironmentVariable("REACT_APP_GANALYTICS_ID")}`);

const analytics = Analytics({
  app: "Optscale",
  plugins: [
    googleAnalytics({
      measurementIds: [getEnvironmentVariable("REACT_APP_GANALYTICS_ID")],
      debug: true
    })
  ]
});

/* Track a page view */
export const trackPage = () => {
  if (identificationLoading || resetLoading) {
    log("%cGA id or reset is loading, track page postponed");
    setTimeout(trackPage, 1000);
    return;
  }

  const storedUser = analytics.user();
  groupLog("GA track page", [
    ["User: ", storedUser],
    ["User traits: ", storedUser.traits],
    ["Campaign:", analytics.getState("context.campaign")],
    ["State", analytics.getState()]
  ]);

  analytics.page();
};

/* Track a custom event */
export const trackEvent = (config) => {
  if (identificationLoading || resetLoading) {
    log("%cGA id is loading, track event postponed");
    setTimeout(() => trackEvent(config), 1000);
    return;
  }

  const { category, action, label, value, nonInteraction } = config;
  if (Object.values(GA_EVENT_CATEGORIES).includes(category)) {
    const eventBody = {
      category,
      label,
      value,
      nonInteraction
    };

    analytics.track(action, eventBody);

    log("%cGA track event", action, eventBody);
  }
};

/**
 * Identify a visitor
 * @param {string} uniqueId Unique id for analytics platform
 * @param {object} newDimensions Information about user
 * @param {string} newDimensions.userId User id in optscale
 * @param {string} [newDimensions.organizationId] Selected Optscale organization id
 */
export const identify = (uniqueId, newDimensions) => {
  const dimensions = {
    uid: newDimensions.userId,
    ...(newDimensions.organizationId ? { orgid: newDimensions.organizationId } : {})
  };
  log("%cGA identify with", dimensions);

  identificationLoading = true;
  analytics.identify(uniqueId, dimensions, {}, () => {
    identificationLoading = false;
    log("%cGA identify completed");
  });
};

/* Reset data if analytics saved uid is different from current one */
export const dropUserIdentificationIfUniqueIdChanged = (currentUid) => {
  const storedUserId = analytics.user().userId;
  // do not reset, if there is no stored userId — that way we can keep one anonId for not signed in and signed in user
  const isUniqueIdChanged = currentUid !== storedUserId && storedUserId !== undefined;
  if (isUniqueIdChanged) {
    log("%cGA different uid, doing analytics storage reset");
    resetLoading = true;
    analytics.reset(() => {
      resetLoading = false;
      log("%cGA analytics storage reset completed");

      // if no user traits were set while reset — identifying user with just uid
      if (!identificationLoading && isEmpty(analytics.user().traits)) {
        log("%cGA no user info was set while storage reset. Identifying user with uid only");
        identify(currentUid, { userId: currentUid });
      }
    });
  }
};
