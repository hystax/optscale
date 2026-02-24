import { AwsConnectionAccessKeyInputs } from "./AwsConnectionAccessKeyInputs";
import {
  AuthenticationTypeSelector,
  getAwsConnectionTypeDescriptions,
  useAuthenticationType,
} from "./AwsConnectionFormElements";
import {
  AUTHENTICATION_TYPES,
  authenticationTypes,
  awsConnectionAssumedRoleDescriptions,
  awsConnectionKeyAccessDescriptions,
  AWS_ROOT_INPUTS_FIELD_NAMES,
} from "./constants";
import { AuthenticationType } from "./types";

export {
  AUTHENTICATION_TYPES,
  AWS_ROOT_INPUTS_FIELD_NAMES,
  authenticationTypes,
  awsConnectionAssumedRoleDescriptions,
  awsConnectionKeyAccessDescriptions,
  getAwsConnectionTypeDescriptions,
  useAuthenticationType,
  AuthenticationTypeSelector,
  AwsConnectionAccessKeyInputs,
};
export type { AuthenticationType };
