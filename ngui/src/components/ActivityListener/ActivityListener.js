import { useEffect, useState } from "react";
import ReactGA from "react-ga";
import { useLocation } from "react-router-dom";
import { isDemo, isProduction } from "urls";
import { GANALYTICS_ID } from "utils/constants";
import { initialize as initializeHotjar } from "utils/hotjar";

export const GA_EVENT_CATEGORIES = Object.freeze({
  DATA_SOURCE: "Data Source",
  USER: "User",
  LIVE_DEMO: "Live Demo",
  ENVIRONMENT: "Environment"
});

const isEligibleEnvironment = () => isProduction() || isDemo();

const initializeAll = () => {
  ReactGA.initialize(GANALYTICS_ID);
  initializeHotjar(1931114, 6);
};

const sendPageView = (location) => {
  const page = `${location.pathname}${location.search}`;
  ReactGA.set({ page });
  ReactGA.pageview(page);
};

const ActivityListener = () => {
  const location = useLocation();

  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (isEligibleEnvironment()) {
      initializeAll();
      setInitialized(true);
    }
  }, []);

  useEffect(() => {
    if (initialized) {
      sendPageView(location);
    }
  }, [location, initialized]);

  return null;
};

export const GAEvent = ({ category, action, label, value, nonInteraction }) => {
  if (Object.values(GA_EVENT_CATEGORIES).includes(category)) {
    const eventBody = {
      category,
      action,
      label,
      value,
      nonInteraction
    };
    if (isEligibleEnvironment()) {
      ReactGA.event(eventBody);
    } else {
      console.log(`Attempting to send a GA event with body: ${JSON.stringify(eventBody)}`);
    }
  }
};

export default ActivityListener;
