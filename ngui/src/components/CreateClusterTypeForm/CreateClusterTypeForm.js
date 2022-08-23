import React from "react";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import PageContentWrapper from "components/PageContentWrapper";
import SubmitButtonLoader from "components/SubmitButtonLoader";
import WrapperCard from "components/WrapperCard";
import { DOCS_HYSTAX_CLUSTERS } from "urls";
import { NameField, TagKeyField } from "./FormElements";

const actionBarDefinition = {
  goBack: true,
  title: {
    messageId: "addClusterTypeTitle",
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
        <WrapperCard className="halfWidth">
          <Typography gutterBottom>
            <FormattedMessage
              id="createClusterTypeDescription"
              values={{
                strong: (chunks) => <strong>{chunks}</strong>,
                link: (chunks) => (
                  <Link data-test-id="link_read_more" href={DOCS_HYSTAX_CLUSTERS} target="_blank" rel="noopener">
                    {chunks}
                  </Link>
                )
              }}
            />
          </Typography>
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
        </WrapperCard>
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
