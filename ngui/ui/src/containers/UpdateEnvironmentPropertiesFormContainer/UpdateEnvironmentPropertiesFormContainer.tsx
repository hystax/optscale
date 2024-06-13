import { useEffect, useRef, useState } from "react";
import { useDispatch } from "react-redux";
import { updateEnvironmentProperty } from "api";
import { UPDATE_ENVIRONMENT_PROPERTY } from "api/restapi/actionTypes";
import EnvironmentPropertyForm from "components/forms/EnvironmentPropertyForm";
import { FormValues } from "components/forms/EnvironmentPropertyForm/types";
import { checkError } from "utils/api";

/**
 * «29/10/2020»
 *
 * There is an error with updating parent's state via onSuccess if TTL of RESOURCE_DETAILS expires when we update environment property
 * > «ReactJS. Warning: Can't perform a React state update on an unmounted component»
 *
 * The reason for the error: when ttl expires we re-request resource details and all content on a page is replaced with loading skeletons.
 * That means that "real" components are getting unmounted, but in the dispatch chain we call onSuccess action which updates state of the parent component
 *
 * Flow:
 * -> Property view -> Open create or edit mode -> Update some property -> TTL of the RESOURCE_DETAILS is expired ->
 * -> content of the page is replaced with loading state -> onSuccess handle is called ->
 * -> onSuccess updated state of the parent component -> Parent component is already unmounted (because of loading) ->
 * -> we get the error
 *
 * In order to fix this, I suppose architectural issue, we use ref to store a flag that indicates if component is mounted.
 * If it is mounted, this means that onSuccess handler can be called with no restrictions
 */
const useIsAllowedToHandleSuccessRef = () => {
  const isMounted = useRef(false);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);

  return isMounted;
};

const UpdateEnvironmentPropertiesFormContainer = ({
  environmentId,
  defaultPropertyName,
  defaultPropertyValue,
  onSuccess,
  onCancel,
  isEdit,
  existingProperties
}) => {
  const dispatch = useDispatch();

  // Need to handle loading state locally since we can dispatch multiple requests with the same API label
  // and entityId will be not enough to get correct loading state
  const [isLoading, setIsLoading] = useState(false);

  const shouldHandleSuccessRef = useIsAllowedToHandleSuccessRef();

  const onSubmit = (formData: FormValues) => {
    setIsLoading(true);
    dispatch((_, getState) => {
      dispatch(updateEnvironmentProperty(environmentId, formData))
        .then(() => setIsLoading(false))
        .then(() => checkError(UPDATE_ENVIRONMENT_PROPERTY, getState()))
        .then(() => {
          if (shouldHandleSuccessRef.current && typeof onSuccess === "function") {
            onSuccess();
          }
        });
    });
  };

  return (
    <EnvironmentPropertyForm
      defaultPropertyName={defaultPropertyName}
      defaultPropertyValue={defaultPropertyValue}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      isEdit={isEdit}
      existingProperties={existingProperties}
    />
  );
};

export default UpdateEnvironmentPropertiesFormContainer;
