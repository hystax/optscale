import React from "react";
import { Alert, Link, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { NEBIUS_CREATE_SERVICE_ACCOUNT, NEBIUS_CREATING_AUTHORIZED_KEYS, NEBIUS_CREATING_STATIC_ACCESS_KEYS } from "urls";

const ServiceAccountCredentialsDescription = () => (
  <Alert severity="info">
    <Typography gutterBottom>
      <FormattedMessage
        id="createNebiusDescription.provideCredentialsForServiceAccount"
        values={{
          strong: (chunks) => <strong>{chunks}</strong>
        }}
      />
    </Typography>
    <Typography gutterBottom>
      <FormattedMessage id="createNebiusDescription.addPermissionsToCloud" />
    </Typography>
    <Typography>
      <FormattedMessage id="createNebiusDescription.nebiusDocumentationReference" />
    </Typography>
    <Typography component="div" gutterBottom>
      <ul
        style={{
          marginTop: "0px",
          marginBottom: "0px"
        }}
      >
        <li>
          <Link href={NEBIUS_CREATE_SERVICE_ACCOUNT} rel="noopener" target="_blank">
            <FormattedMessage id="createServiceAccount" />
          </Link>
        </li>
        <li>
          <Link href={NEBIUS_CREATING_AUTHORIZED_KEYS} rel="noopener" target="_blank">
            <FormattedMessage id="creatingAuthorizedKeys" />
          </Link>
        </li>
        <li>
          <Link href={NEBIUS_CREATING_STATIC_ACCESS_KEYS} rel="noopener" target="_blank">
            <FormattedMessage id="creatingStaticAccessKeys" />
          </Link>
        </li>
      </ul>
    </Typography>
  </Alert>
);

export default ServiceAccountCredentialsDescription;
