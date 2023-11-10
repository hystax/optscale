import { Box, Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import MlRunsetConfigurationForm from "components/MlRunsetConfigurationForm";
import PageContentWrapper from "components/PageContentWrapper";
import { ML_RUNSET_TEMPLATES, getMlRunsetTemplateUrl } from "urls";

const MlRunsetConfiguration = ({ runsetTemplate, latestRunset, onSubmit, onCancel, isLoading = {} }) => (
  <>
    <ActionBar
      data={{
        breadcrumbs: [
          <Link key={1} to={ML_RUNSET_TEMPLATES} component={RouterLink}>
            <FormattedMessage id="runsetTemplatesTitle" />
          </Link>,
          <Link key={2} to={getMlRunsetTemplateUrl(runsetTemplate.id)} component={RouterLink}>
            {runsetTemplate.name}
          </Link>
        ],
        title: {
          messageId: "runsetConfiguration",
          isLoading: isLoading.isGetRunsetTemplateLoading
        }
      }}
    />
    <PageContentWrapper>
      <Box
        sx={{
          width: { md: "50%" }
        }}
      >
        <MlRunsetConfigurationForm
          runsetTemplate={runsetTemplate}
          latestRunset={latestRunset}
          onSubmit={onSubmit}
          onCancel={onCancel}
          isLoading={isLoading}
        />
      </Box>
    </PageContentWrapper>
  </>
);

export default MlRunsetConfiguration;
