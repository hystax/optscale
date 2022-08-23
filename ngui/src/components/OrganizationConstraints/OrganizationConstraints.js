import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import ActionBar from "components/ActionBar";
import OrganizationConstraintsTable from "components/OrganizationConstraintsTable";
import PageContentWrapper from "components/PageContentWrapper";
import WrapperCard from "components/WrapperCard";
import { SPACING_2 } from "utils/layouts";

const OrganizationConstraints = ({ actionBarDefinition, constraints, addButtonLink, isLoading = false }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <WrapperCard>
        <Grid container spacing={SPACING_2}>
          <Grid item xs={12}>
            <OrganizationConstraintsTable constraints={constraints} isLoading={isLoading} addButtonLink={addButtonLink} />
          </Grid>
        </Grid>
      </WrapperCard>
    </PageContentWrapper>
  </>
);

OrganizationConstraints.propTypes = {
  actionBarDefinition: PropTypes.object.isRequired,
  constraints: PropTypes.array.isRequired,
  addButtonLink: PropTypes.string.isRequired,
  isLoading: PropTypes.bool
};

export default OrganizationConstraints;
