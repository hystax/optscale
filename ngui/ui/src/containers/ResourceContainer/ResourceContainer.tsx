import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getResource, updateResourceVisibility } from "api";
import { GET_RESOURCE, UPDATE_RESOURCE_VISIBILITY } from "api/restapi/actionTypes";
import Resource from "components/Resource";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const details = true;

const ResourceContainer = ({ resourceId }) => {
  const {
    apiData: { resource = {} }
  } = useApiData(GET_RESOURCE);

  const { isLoading: isLoadingPatch } = useApiState(UPDATE_RESOURCE_VISIBILITY);
  const { isLoading: isGetResourceLoading, shouldInvoke } = useApiState(GET_RESOURCE, { resourceId, details });

  const dispatch = useDispatch();

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getResource(resourceId, details));
    }
  }, [shouldInvoke, dispatch, resourceId]);

  const patchResource = (recommendationType, action) =>
    dispatch(
      updateResourceVisibility(resourceId, {
        recommendation: recommendationType,
        action
      })
    );

  return (
    <Resource
      resource={resource}
      patchResource={patchResource}
      isLoadingPatch={isLoadingPatch}
      isGetResourceLoading={isGetResourceLoading}
    />
  );
};

export default ResourceContainer;
