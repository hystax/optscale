import React from "react";
import S3DuplicateFinderSettingsForm from "components/S3DuplicateFinderSettingsForm";
import { useS3DuplicatesSettings } from "hooks/useS3DuplicatesSettings";
import OrganizationOptionsService from "services/OrganizationOptionsService";

const S3DuplicateFinderSettingsFormContainer = ({ closeSideModal }) => {
  const {
    isLoading: isGetDataLoading,
    settings: {
      thresholds: { requiringAttention, critical }
    }
  } = useS3DuplicatesSettings();

  const { useUpdateS3DuplicatedOrganizationSettings } = OrganizationOptionsService();

  const { onUpdate, isLoading: isUpdateLoading } = useUpdateS3DuplicatedOrganizationSettings();

  const onSubmit = (params) => {
    onUpdate(params).then(closeSideModal);
  };

  return (
    <S3DuplicateFinderSettingsForm
      requiringAttention={requiringAttention}
      critical={critical}
      onCancel={closeSideModal}
      onSubmit={onSubmit}
      isLoadingProps={{
        isGetDataLoading,
        isSubmitLoading: isUpdateLoading
      }}
    />
  );
};

export default S3DuplicateFinderSettingsFormContainer;
