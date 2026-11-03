import { FocusConfig } from "graphql/__generated__/hooks/restapi";
import { CONNECTION_MODES, DEFAULT_FILE_PATTERN, FIELD_NAMES } from "./constants";

const getOptionalString = (value: unknown) => (typeof value === "string" ? value.trim() : "");

// Empty endpoint means AWS S3. Like the server, a URL needs the https scheme and a host
export const isHttpsEndpoint = (value: string) => {
  const endpoint = value.trim();

  if (endpoint === "") {
    return true;
  }

  try {
    const url = new URL(endpoint);
    return url.protocol === "https:" && url.hostname !== "";
  } catch {
    return false;
  }
};

// Keys are set together or not at all, no keys mean anonymous access
export const isKeyPairConsistent = (accessKeyId: string, secretAccessKey: string) =>
  (accessKeyId.trim() === "") === (secretAccessKey.trim() === "");

export const getFocusConfigParams = (formData: Record<string, unknown>) => {
  if (formData[FIELD_NAMES.CONNECTION_MODE] !== CONNECTION_MODES.BUCKET) {
    return {};
  }

  const optionalParams = Object.entries({
    bucket_prefix: getOptionalString(formData[FIELD_NAMES.BUCKET_PREFIX]),
    s3_endpoint: getOptionalString(formData[FIELD_NAMES.S3_ENDPOINT]),
    region_name: getOptionalString(formData[FIELD_NAMES.REGION_NAME]),
    file_pattern: getOptionalString(formData[FIELD_NAMES.FILE_PATTERN]),
  }).filter(([, value]) => value !== "");

  const accessKeyId = getOptionalString(formData[FIELD_NAMES.ACCESS_KEY_ID]);
  const secretAccessKey = getOptionalString(formData[FIELD_NAMES.SECRET_ACCESS_KEY]);

  return {
    bucket_name: getOptionalString(formData[FIELD_NAMES.BUCKET_NAME]),
    ...Object.fromEntries(optionalParams),
    // No keys mean anonymous access
    ...(accessKeyId && secretAccessKey
      ? { credentials: { access_key_id: accessKeyId, secret_access_key: secretAccessKey } }
      : {}),
  };
};

// On update the API replaces the whole config, but ignores an empty one. A manual upload config therefore
// carries the default file pattern (not used without a bucket), so that switching from a bucket removes it.
export const getFocusUpdateConfigParams = (formData: Record<string, unknown>) =>
  formData[FIELD_NAMES.CONNECTION_MODE] === CONNECTION_MODES.BUCKET
    ? getFocusConfigParams(formData)
    : { file_pattern: DEFAULT_FILE_PATTERN };

// The API never returns the keys, so they always start empty. The file pattern of a manual upload config
// was sent by getFocusUpdateConfigParams, not entered by the user, so it is not prefilled.
export const getFocusDefaultValues = (config: FocusConfig = {}) => ({
  [FIELD_NAMES.CONNECTION_MODE]: config.bucket_name ? CONNECTION_MODES.BUCKET : CONNECTION_MODES.MANUAL_UPLOAD,
  [FIELD_NAMES.BUCKET_NAME]: config.bucket_name ?? "",
  [FIELD_NAMES.BUCKET_PREFIX]: config.bucket_prefix ?? "",
  [FIELD_NAMES.S3_ENDPOINT]: config.s3_endpoint ?? "",
  [FIELD_NAMES.REGION_NAME]: config.region_name ?? "",
  [FIELD_NAMES.ACCESS_KEY_ID]: "",
  [FIELD_NAMES.SECRET_ACCESS_KEY]: "",
  [FIELD_NAMES.FILE_PATTERN]: (config.bucket_name && config.file_pattern) || "",
});
