import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import EnabledConstraints from "components/EnabledConstraints";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PoolConstraintContainer from "containers/PoolConstraintContainer";
import { DOCS_HYSTAX_RESOURCE_CONSTRAINTS } from "urls";
import useStyles from "./PoolConstraints.styles";

const PoolConstraints = ({ isLoading, policies, poolId }) => {
  const { classes } = useStyles();
  return (
    <>
      <EnabledConstraints
        render={(type) => (
          <div className={classes.item}>
            <PoolConstraintContainer
              key={type}
              policy={policies.find((policy) => type === policy.type && poolId === policy.pool_id)}
              poolId={poolId}
              isLoading={isLoading}
              policyType={type}
            />
          </div>
        )}
      />
      <div>
        <InlineSeverityAlert
          messageId="poolConstraintsDescription"
          messageDataTestId="p_alert"
          messageValues={{
            link: (chunks) => (
              <Link data-test-id="link_help" href={DOCS_HYSTAX_RESOURCE_CONSTRAINTS} target="_blank" rel="noopener">
                {chunks}
              </Link>
            )
          }}
        />
      </div>
    </>
  );
};

PoolConstraints.propTypes = {
  isLoading: PropTypes.bool,
  policies: PropTypes.array,
  poolId: PropTypes.string
};

export default PoolConstraints;
