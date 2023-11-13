import { useMemo } from "react";
import { GET_ORGANIZATION_PERSPECTIVES } from "api/restapi/actionTypes";
import { parseJSON } from "utils/strings";
import { validatePerspectiveSchema } from "utils/validation";
import { useApiData } from "./useApiData";

const validatePerspectives = (perspectives) => {
  const validPerspectives = {};
  const invalidPerspectives = {};

  Object.entries(perspectives).forEach(([perspectiveName, perspectivePayload]) => {
    const [isValid] = validatePerspectiveSchema(perspectivePayload);
    (isValid ? validPerspectives : invalidPerspectives)[perspectiveName] = perspectivePayload;
  });

  return {
    validPerspectives,
    invalidPerspectives
  };
};

export const useOrganizationPerspectives = () => {
  const {
    apiData: { value = "{}" }
  } = useApiData(GET_ORGANIZATION_PERSPECTIVES, {});

  return useMemo(() => {
    const perspectivesJson = parseJSON(value);

    const { validPerspectives, invalidPerspectives } = validatePerspectives(perspectivesJson);

    return {
      allPerspectives: perspectivesJson,
      validPerspectives,
      invalidPerspectives
    };
  }, [value]);
};
