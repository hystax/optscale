import { useEffect, useMemo, useState } from "react";
import { useDispatch } from "react-redux";
import { getWebhooks, createWebhook, updateWebhook, getResourceAllowedActions, deleteWebhook } from "api";
import { GET_WEBHOOKS, CREATE_WEBHOOK, UPDATE_WEBHOOK, DELETE_WEBHOOK } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { checkError } from "utils/api";

export const BOOKING_ACQUIRE = "booking_acquire";
export const BOOKING_RELEASE = "booking_release";

export const ACTIONS = Object.freeze({
  [BOOKING_ACQUIRE]: "acquireWebhook",
  [BOOKING_RELEASE]: "releaseWebhook"
});

const useGet = ({ objectId, objectType }) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: webhooks } = useApiData(GET_WEBHOOKS, []);

  const requestParams = useMemo(
    () => ({
      objectId,
      objectType
    }),
    [objectId, objectType]
  );

  const {
    isLoading: isGetWebhooksLoading,
    entityId,
    shouldInvoke
  } = useApiState(GET_WEBHOOKS, {
    ...requestParams,
    organizationId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch((_, getState) => {
        dispatch(getWebhooks(organizationId, requestParams))
          .then(() => checkError(GET_WEBHOOKS, getState()))
          // TODO: for now it is always resource ID, but technically should map based on objectType
          .then(() => dispatch(getResourceAllowedActions(requestParams.objectId)));
      });
    }
  }, [dispatch, organizationId, requestParams, shouldInvoke]);

  return { isGetWebhooksLoading, entityId, webhooks };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const [isLoading, setIsLoading] = useState(false);

  const create = ({ objectId, objectType, url, action, onSuccess }) => {
    // Cannot use isLoading from storage, because there are might be multiple webhook forms (currently 2), and there is no way to distinguish their loading state (all of them will go into loading)
    // Do not need to set isLoading back to false, since component unmounts anyway
    setIsLoading(true);
    dispatch((_, getState) => {
      dispatch(createWebhook(organizationId, { objectId, objectType, url, action }))
        .then(() => checkError(CREATE_WEBHOOK, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        });
    });
  };

  return { create, isCreateWebhookLoading: isLoading };
};

const useUpdate = () => {
  const dispatch = useDispatch();

  const [isLoading, setIsLoading] = useState(false);

  const update = ({ webhookId, url, onSuccess }) => {
    // Cannot use isLoading from storage, because there are might be multiple webhook forms (currently 2), and there is no way to distinguish their loading state (all of them will go into loading)
    // Do not need to set isLoading back to false, since component unmounts anyway
    setIsLoading(true);
    dispatch((_, getState) => {
      dispatch(updateWebhook(webhookId, { url }))
        .then(() => checkError(UPDATE_WEBHOOK, getState()))
        .then(() => {
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        });
    });
  };

  return { update, isUpdateWebhookLoading: isLoading };
};

const useDelete = () => {
  const dispatch = useDispatch();

  const [isLoading, setIsLoading] = useState(false);

  const deleteWebhookAction = ({ webhookId, onSuccess }) => {
    setIsLoading(true);
    dispatch((_, getState) => {
      dispatch(deleteWebhook(webhookId))
        .then(() => checkError(DELETE_WEBHOOK, getState()))
        .then(() => {
          setIsLoading(false);
          if (typeof onSuccess === "function") {
            onSuccess();
          }
        });
    });
  };

  return { deleteWebhook: deleteWebhookAction, isRemoveWebhookLoading: isLoading };
};

function WebhooksService() {
  return { useGet, useCreate, useUpdate, useDelete };
}

export default WebhooksService;
