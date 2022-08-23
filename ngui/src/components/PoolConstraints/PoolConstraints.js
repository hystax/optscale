import React from "react";
import Grid from "@mui/material/Grid";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import EnabledConstraints from "components/EnabledConstraints";
import PoolConstraintContainer from "containers/PoolConstraintContainer";
import { DOCS_HYSTAX_RESOURCE_CONSTRAINTS } from "urls";
import { SPACING_2 } from "utils/layouts";

const PoolConstraints = ({ isLoading, policies, poolId }) => (
  <Grid container direction="row" justifyContent="flex-start" spacing={SPACING_2}>
    <Grid item xs={12}>
      <Typography data-test-id="p_enabled_constraints">
        <FormattedMessage id="poolConstraintsDescription1" />
      </Typography>
      <Typography data-test-id="p_alert">
        <FormattedMessage id="poolConstraintsDescription2" />
      </Typography>
      <Typography>
        <FormattedMessage
          id="linkedText"
          values={{
            text: <FormattedMessage id="getMoreHelp" />,
            link: (chunks) => (
              <Link data-test-id="link_help" href={DOCS_HYSTAX_RESOURCE_CONSTRAINTS} target="_blank" rel="noopener">
                {chunks}
              </Link>
            )
          }}
        />
      </Typography>
    </Grid>
    <EnabledConstraints
      render={(type) => (
        <Grid item>
          <PoolConstraintContainer
            key={type}
            policy={policies.find((policy) => type === policy.type && poolId === policy.pool_id)}
            poolId={poolId}
            isLoading={isLoading}
            policyType={type}
          />
        </Grid>
      )}
    />
  </Grid>
);

PoolConstraints.propTypes = {
  isLoading: PropTypes.bool,
  policies: PropTypes.array,
  poolId: PropTypes.string
};

export default PoolConstraints;
