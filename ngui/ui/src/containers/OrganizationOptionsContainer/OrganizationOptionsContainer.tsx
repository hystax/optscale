import { useState, useEffect, useCallback } from "react";
import { useDispatch } from "react-redux";
import { GET_ORGANIZATION_OPTION } from "api/restapi/actionTypes";
import OrganizationOptions from "components/OrganizationOptions";
import { useInitialMount } from "hooks/useInitialMount";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { isError } from "utils/api";
import { getQueryParams, updateQueryParams } from "utils/network";

const OPTION = "option";

const OrganizationOptionsContainer = () => {
  const dispatch = useDispatch();
  const { isInitialMount, setIsInitialMount } = useInitialMount();
  const [requestedOption, setRequestedOption] = useState();

  const { [OPTION]: optionQueryParam } = getQueryParams();
  const [expandedOption, setExpandedOption] = useState(optionQueryParam);

  useEffect(() => {
    updateQueryParams({ [OPTION]: expandedOption });
  }, [expandedOption]);

  const { useGet, useGetOption, useUpdateOption } = OrganizationOptionsService();
  const { isGetOrganizationOptionsLoading, options } = useGet();
  const { isGetOrganizationOptionLoading, value, getOption } = useGetOption();
  const { isUpdateOrganizationOptionLoading, updateOption } = useUpdateOption();

  const getOptionCallback = useCallback(
    (optionName) =>
      dispatch((_, getState) => {
        getOption(optionName).then(() => {
          if (!isError(GET_ORGANIZATION_OPTION, getState())) {
            setExpandedOption(optionName);
          }
        });
      }),
    [dispatch, getOption]
  );

  useEffect(() => {
    if (isInitialMount && expandedOption) {
      setRequestedOption(expandedOption);
      getOptionCallback(expandedOption);
    }
    setIsInitialMount(false);
  }, [getOptionCallback, expandedOption, isGetOrganizationOptionsLoading, isInitialMount, setIsInitialMount]);

  const handleOptionExpand = useCallback(
    (optionName) => {
      // Identify a requested (clicked) option name to display a loader next to it. It will be used in conjunction with isGetOrganizationOptionLoading
      setRequestedOption(optionName);
      // Close any expanded panel and if a clicked one is different from the last, call for it
      setExpandedOption(undefined);
      if (expandedOption !== optionName) {
        getOptionCallback(optionName);
      }
    },
    [getOptionCallback, expandedOption]
  );

  const saveOption = (optionName, updatedValue) => {
    updateOption(optionName, updatedValue);
  };

  return (
    <OrganizationOptions
      options={options}
      value={value}
      requestedOption={requestedOption}
      expandedOption={expandedOption}
      handleExpand={handleOptionExpand}
      isLoadingProps={{
        isGetOrganizationOptionsLoading,
        isGetOrganizationOptionLoading,
        isUpdateOrganizationOptionLoading
      }}
      onSave={saveOption}
    />
  );
};

export default OrganizationOptionsContainer;
