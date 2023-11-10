import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import { TABS as RESOURCE_LIFECYCLE_TABS } from "components/ResourceLifecycle/ResourceLifecycle";
import CreatePoolPolicyFormContainer from "containers/CreatePoolPolicyFormContainer";
import { RESOURCE_LIFECYCLE, getResourceLifecycleUrl } from "urls";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={RESOURCE_LIFECYCLE} component={RouterLink}>
      <FormattedMessage id="resourceLifecycleTitle" />
    </Link>,
    <Link key={2} to={getResourceLifecycleUrl(RESOURCE_LIFECYCLE_TABS.POOL_POLICIES)} component={RouterLink}>
      <FormattedMessage id="poolPolicies" />
    </Link>
  ],
  title: {
    text: <FormattedMessage id="createPoolPolicyTitle" />,
    dataTestId: "lbl_create_pool_policy"
  }
};

const CreatePoolPolicy = () => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <CreatePoolPolicyFormContainer />
    </PageContentWrapper>
  </>
);

export default CreatePoolPolicy;
