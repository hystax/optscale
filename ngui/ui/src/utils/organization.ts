import { intl } from "translations/react-intl-config";
import { sliceByLimitWithEllipsis } from "./strings";

const INACTIVE_SUFFIX = ` (${intl.formatMessage({ id: "inactive" })})`;

type GetOrganizationDisplayNameParams = {
  name: string;
  maxLength: number;
  isInactive?: boolean;
};

export const getOrganizationDisplayName = ({ name, isInactive = false, maxLength }: GetOrganizationDisplayNameParams) => {
  const displayName = isInactive ? `${name}${INACTIVE_SUFFIX}` : name;
  const effectiveMaxLength = isInactive ? maxLength - INACTIVE_SUFFIX.length : maxLength;

  const isNameLong = displayName.length > maxLength;
  return {
    displayName: isNameLong
      ? `${sliceByLimitWithEllipsis(name, effectiveMaxLength)}${isInactive ? INACTIVE_SUFFIX : ""}`
      : displayName,
    isNameLong,
    originalName: name,
  };
};
