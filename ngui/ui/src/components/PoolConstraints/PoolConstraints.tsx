import { Box, Stack } from "@mui/material";
import Link from "@mui/material/Link";
import EnabledConstraints from "components/EnabledConstraints";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PoolConstraintContainer from "containers/PoolConstraintContainer";
import { DOCS_HYSTAX_RESOURCE_CONSTRAINTS } from "urls";
import { SPACING_1, SPACING_2 } from "utils/layouts";

const PoolConstraints = ({ isLoading, policies, poolId }) => (
  <Stack spacing={SPACING_2}>
    <Box display="flex" flexWrap="wrap" columnGap={SPACING_2} rowGap={SPACING_1}>
      <EnabledConstraints
        render={(type) => (
          <div>
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
    </Box>
    <Box>
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
    </Box>
  </Stack>
);

export default PoolConstraints;
