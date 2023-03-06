import React, { useEffect, useState } from "react";
import { Box } from "@mui/material";
import Tab from "@mui/material/Tab";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import TabContent from "components/TabContent";
import TabsComponent from "components/Tabs";
import TabsLoader from "components/TabsLoader";
import { TAB_QUERY_PARAM_NAME } from "utils/constants";
import { getQueryParams, removeQueryParam, updateQueryParams } from "utils/network";

// TODO: Investigate how to make a component manageable
const getActiveTab = (activeTabState, externalActiveTab, tabs) => {
  if (!externalActiveTab) {
    return activeTabState;
  }
  const { renderCondition: currentActiveTabRenderCondition } = tabs.find((el) => el.title === externalActiveTab) ?? {};
  // if it is not possible to render current active tab at the moment
  if (typeof currentActiveTabRenderCondition === "function" && !currentActiveTabRenderCondition()) {
    // find first tab that can be rendered
    const alternativeTab = tabs.find((el) => {
      if (typeof el.renderCondition === "function") {
        return el.title !== externalActiveTab && el.renderCondition();
      }
      return el.title !== externalActiveTab;
    });
    return alternativeTab.title;
  }
  return externalActiveTab;
};

const getBuildedTabs = ({ tabs, name, activeTab, keepTabContentMounted = false }) =>
  tabs.reduce(
    (result, item) => {
      const shouldRender = typeof item.renderCondition === "function" ? item.renderCondition() : true;
      return {
        ...result,
        tabHeaders: [
          ...result.tabHeaders,
          shouldRender ? (
            <Tab
              key={item.title}
              value={item.title}
              icon={item.icon}
              iconPosition={item.iconPosition}
              label={<FormattedMessage id={item.title} />}
              id={`${name}-tab-${item.title}`}
              aria-controls={`${name}-tabpanel-${item.title}`}
              data-test-id={item.dataTestId}
              style={{ fontWeight: item.isBold && "bold" }}
            />
          ) : null
        ],
        tabContents: [
          ...result.tabContents,
          shouldRender ? (
            <TabContent
              key={`tabcontent-${item.title}`}
              value={activeTab}
              index={item.title}
              id={`${name}-tabpanel-${item.title}`}
              ariaLabelledby={`${name}-tab-${item.title}`}
            >
              {activeTab === item.title || keepTabContentMounted ? item.node : null}
            </TabContent>
          ) : null
        ]
      };
    },
    { tabHeaders: [], tabContents: [] }
  );

const Tabs = ({ tabsProps, headerAdornment, headerSx }) => {
  const {
    tabs,
    defaultTab,
    activeTab: externalActiveTab,
    handleChange: externalHandleChange,
    name,
    queryTabName,
    queryParamsOnChangeBlacklist = [],
    keepTabContentMounted = false
  } = tabsProps;
  const tabName = queryTabName || TAB_QUERY_PARAM_NAME;
  const { [tabName]: tab = defaultTab } = getQueryParams();
  const [currentQueryTab, setCurrentQueryTab] = useState(tab);
  const [activeTabState, setActiveTab] = useState(tab);

  useEffect(() => {
    const newTab = externalActiveTab || activeTabState;
    updateQueryParams({ [tabName]: newTab });
    setCurrentQueryTab(externalActiveTab || activeTabState);
  }, [activeTabState, tabName, externalActiveTab]);

  useEffect(() => {
    if (tab !== currentQueryTab) {
      setActiveTab(tab);
    }
  }, [tab, currentQueryTab]);

  const handleChange = (event, value) => {
    setActiveTab(value);
    // Query parameters to remove on tab change
    queryParamsOnChangeBlacklist.forEach((param) => removeQueryParam(param));
  };

  const activeTab = getActiveTab(activeTabState, externalActiveTab, tabs);

  const { tabHeaders, tabContents } = getBuildedTabs({ tabs, name, activeTab, keepTabContentMounted });

  return (
    <>
      <Box sx={{ ...headerSx, borderBottom: 1, borderColor: "divider" }}>
        <TabsComponent area-label={`${name}-tabs`} value={activeTab} onChange={externalHandleChange || handleChange}>
          {tabHeaders}
        </TabsComponent>
        {headerAdornment}
      </Box>
      {tabContents}
    </>
  );
};

const TabsWrapper = ({ tabsProps, isLoading, headerAdornment = null, headerSx = {} }) => {
  const { tabs } = tabsProps;

  if (isLoading) {
    return <TabsLoader tabsCount={tabs.length} />;
  }

  return <Tabs tabsProps={tabsProps} headerAdornment={headerAdornment} headerSx={headerSx} />;
};

TabsWrapper.propTypes = {
  tabsProps: PropTypes.shape({
    tabs: PropTypes.array.isRequired,
    defaultTab: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    queryTabName: PropTypes.string,
    activeTab: PropTypes.string,
    handleChange: PropTypes.func,
    queryParamsOnChangeBlacklist: PropTypes.array,
    keepTabContentMounted: PropTypes.bool
  }).isRequired,
  isLoading: PropTypes.bool,
  headerAdornment: PropTypes.node,
  headerSx: PropTypes.object
};

export default TabsWrapper;
