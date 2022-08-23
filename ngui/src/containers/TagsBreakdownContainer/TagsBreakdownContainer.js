import React, { useMemo, useState } from "react";
import PropTypes from "prop-types";
import TagsBreakdown from "components/TagsBreakdown";
import ResourcesCountBreakdownService from "services/ResourcesCountBreakdownService";
import TagsBreakdownService from "services/TagsBreakdownService";
import { EMPTY_UUID } from "utils/constants";

const useSelectedTagSetting = () => {
  const [selectedTag, setSelectedTag] = useState(undefined);

  const updateSelectedTag = (key) => {
    setSelectedTag((currentSetting) => {
      if (key === currentSetting) {
        return undefined;
      }
      return key;
    });
  };

  return {
    selectedTag,
    updateSelectedTag
  };
};

const TagsBreakdownContainer = ({ requestParams }) => {
  const { selectedTag, updateSelectedTag } = useSelectedTagSetting();

  const { useGet: useTagsBreakdownGet } = TagsBreakdownService();

  const {
    isGetTagsBreakdownLoading,
    data: { breakdown: tagsBreakdown }
  } = useTagsBreakdownGet(requestParams);
  const resourceCountRequestParams = useMemo(
    () => ({
      ...requestParams,
      tag: selectedTag === null ? EMPTY_UUID : selectedTag
    }),
    [requestParams, selectedTag]
  );
  const { useGet: useResourcesCountBreakdownGet } = ResourcesCountBreakdownService();

  const {
    isGetResourceCountBreakdownLoading,
    data: { breakdown }
  } = useResourcesCountBreakdownGet(undefined, resourceCountRequestParams);

  return (
    <TagsBreakdown
      data={tagsBreakdown || []}
      chartData={breakdown || {}}
      isLoading={isGetTagsBreakdownLoading}
      isChartLoading={isGetResourceCountBreakdownLoading}
      selectedTag={selectedTag}
      updateSelectedTag={updateSelectedTag}
      appliedRange={{
        startSecondsTimestamp: Number(requestParams.startDate),
        endSecondsTimestamp: Number(requestParams.endDate)
      }}
    />
  );
};

TagsBreakdownContainer.propTypes = {
  requestParams: PropTypes.object.isRequired
};

export default TagsBreakdownContainer;
