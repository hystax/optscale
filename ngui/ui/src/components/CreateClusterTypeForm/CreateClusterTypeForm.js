import React from "react";
import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PageContentWrapper from "components/PageContentWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import { CLUSTER_TYPES, DOCS_HYSTAX_CLUSTERS, RESOURCES } from "urls";
import { SPACING_1 } from "utils/layouts";
import { NameField, TagKeyField } from "./FormElements";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={RESOURCES} component={RouterLink}>
      <FormattedMessage id="resources" />
    </Link>,
    <Link key={2} to={CLUSTER_TYPES} component={RouterLink}>
      <FormattedMessage id="clusterTypesTitle" />
    </Link>
  ],
  title: {
    text: <FormattedMessage id="addClusterTypeTitle" />,
    dataTestId: "lbl_add_cluster_type"
  }
};

const CreateClusterTypeForm = ({ onSubmit, onCancel, isSubmitLoading = false }) => {
  const methods = useForm();
  const { handleSubmit } = methods;

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Box sx={{ width: { md: "50%" }, mb: SPACING_1 }}>
          <FormProvider {...methods}>
            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              <NameField />
              <TagKeyField />
              <FormButtonsWrapper>
                <SubmitButtonLoader messageId="create" isLoading={isSubmitLoading} dataTestId="btn_create" />
                <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
              </FormButtonsWrapper>
            </form>
          </FormProvider>
        </Box>
        <InlineSeverityAlert
          messageId="createClusterTypeDescription"
          messageValues={{
            strong: (chunks) => <strong>{chunks}</strong>,
            link: (chunks) => (
              <Link data-test-id="link_read_more" href={DOCS_HYSTAX_CLUSTERS} target="_blank" rel="noopener">
                {chunks}
              </Link>
            )
          }}
        />
      </PageContentWrapper>
    </>
  );
};

CreateClusterTypeForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isSubmitLoading: PropTypes.bool
};

export default CreateClusterTypeForm;
