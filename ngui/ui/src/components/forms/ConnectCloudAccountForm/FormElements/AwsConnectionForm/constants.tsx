import React from "react";
import { DOCS_HYSTAX_CONNECT_AWS_ROOT } from "urls";
import { AWS_CNR, CONNECTION_TYPES } from "utils/constants";
import { AwsTypeDescription } from "./AwsConnectionFormElements";

export const AUTHENTICATION_TYPES = Object.freeze({
  ASSUMED_ROLE: "assumedRole",
  ACCESS_KEY: "accessKey",
});

export const authenticationTypes = [
  {
    authenticationType: AUTHENTICATION_TYPES.ASSUMED_ROLE,
    messageId: "assumedRole",
    cloudType: AWS_CNR,
  },
  { authenticationType: AUTHENTICATION_TYPES.ACCESS_KEY, messageId: "accessKey", cloudType: AWS_CNR },
];

export const AWS_ROOT_INPUTS_FIELD_NAMES = {
  IS_FIND_REPORT: "isFindReport",
  CONFIG_SCHEME: "configScheme",
};

const awsDefaultAssumedRoleDescriptions = [
  <AwsTypeDescription key="1" messageId="createAwsMemberAssumedRoleDescriptions" />,
  <AwsTypeDescription
    key="2"
    messageId="createAwsDefaultAssumedRoleDocumentationReference3"
    linkUrl={DOCS_HYSTAX_CONNECT_AWS_ROOT}
  />,
];

const awsDefaultAccessKeyDescriptions = [
  <AwsTypeDescription
    key="1"
    messageId="createAwsDefaultAssumedRoleDocumentationReference1"
    linkUrl={DOCS_HYSTAX_CONNECT_AWS_ROOT}
    linkDisplayBlock
    type="warning"
  />,
  <AwsTypeDescription key="2" messageId="createAwsDefaultAssumedRoleDocumentationReference2" />,
  <AwsTypeDescription
    key="3"
    messageId="createAwsDefaultAssumedRoleDocumentationReference3"
    linkUrl={DOCS_HYSTAX_CONNECT_AWS_ROOT}
  />,
];

const awsMemberAccessKeyDescriptions = [
  <AwsTypeDescription
    key="1"
    messageId="createAwsDefaultAssumedRoleDocumentationReference1"
    linkUrl={DOCS_HYSTAX_CONNECT_AWS_ROOT}
    linkDisplayBlock
    type="warning"
  />,
  <AwsTypeDescription key="2" messageId="createAwsDefaultAssumedRoleDocumentationReference4" />,
  <AwsTypeDescription
    key="3"
    messageId="createAwsDefaultAssumedRoleDocumentationReference3"
    linkUrl={DOCS_HYSTAX_CONNECT_AWS_ROOT}
    linkDisplayBlock={false}
  />,
];

export const awsConnectionAssumedRoleDescriptions = {
  [CONNECTION_TYPES.AWS_MANAGEMENT]: awsDefaultAssumedRoleDescriptions,
  [CONNECTION_TYPES.AWS_MEMBER]: awsDefaultAssumedRoleDescriptions,
};

export const awsConnectionKeyAccessDescriptions = {
  [CONNECTION_TYPES.AWS_MANAGEMENT]: awsDefaultAccessKeyDescriptions,
  [CONNECTION_TYPES.AWS_MEMBER]: awsMemberAccessKeyDescriptions,
};
