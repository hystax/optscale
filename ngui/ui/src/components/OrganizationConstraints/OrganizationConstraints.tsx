import Grid from "@mui/material/Grid";
import ActionBar from "components/ActionBar";
import OrganizationConstraintsTable from "components/OrganizationConstraintsTable";
import PageContentWrapper from "components/PageContentWrapper";
import { SPACING_2 } from "utils/layouts";

const OrganizationConstraints = ({ actionBarDefinition, constraints, addButtonLink, isLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Grid container spacing={SPACING_2}>
        <Grid item xs={12}>
          <OrganizationConstraintsTable constraints={constraints} isLoading={isLoading} addButtonLink={addButtonLink} />
        </Grid>
      </Grid>
    </PageContentWrapper>
  </>
);

export default OrganizationConstraints;
