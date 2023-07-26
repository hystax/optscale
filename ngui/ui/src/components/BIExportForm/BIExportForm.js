import React, { useEffect } from "react";
import { Box, FormLabel, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { BI_EXPORT_STORAGE_TYPE } from "utils/biExport";
import {
  StorageTypeSelectorField,
  FIELD_NAMES,
  NameField,
  ExportedDaysField,
  AwsAccessKeyIdField,
  AwsSecretAccessKeyField,
  BucketNameField,
  S3PrefixField,
  ConnectionStringField,
  ContainerField,
  FormButtons
} from "./FormElements";

const {
  STORAGE_TYPE_FIELD_NAME,
  NAME_FIELD_NAME,
  EXPORTED_DAYS_FIELD_NAME,
  AWS_ACCESS_KEY_ID_FIELD_NAME,
  AWS_SECRET_ACCESS_KEY_FIELD_NAME,
  BUCKET_NAME_FIELD_NAME,
  S3_PATH_FIELD_NAME,
  CONNECTION_STRING_FIELD_NAME,
  CONTAINER_FIELD_NAME
} = FIELD_NAMES;

const BIExportForm = ({ defaultValues, isLoadingProps, onSubmit, onCancel, isEdit = false }) => {
  const methods = useForm({
    defaultValues
  });

  const { isSubmitLoading, isGetDataLoading } = isLoadingProps;

  const { handleSubmit, reset, watch } = methods;

  const storageType = watch(STORAGE_TYPE_FIELD_NAME);

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...defaultValues
    }));
  }, [defaultValues, reset]);

  const submitHandler = (formData) => {
    const params = {
      name: formData[NAME_FIELD_NAME],
      type: isEdit ? undefined : formData[STORAGE_TYPE_FIELD_NAME],
      days: Number(formData[EXPORTED_DAYS_FIELD_NAME]),
      meta: {
        ...(formData[STORAGE_TYPE_FIELD_NAME] === BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT
          ? {
              access_key_id: formData[AWS_ACCESS_KEY_ID_FIELD_NAME],
              secret_access_key: formData[AWS_SECRET_ACCESS_KEY_FIELD_NAME],
              bucket: formData[BUCKET_NAME_FIELD_NAME],
              s3_prefix: formData[S3_PATH_FIELD_NAME] || undefined
            }
          : {}),
        ...(formData[STORAGE_TYPE_FIELD_NAME] === BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT
          ? {
              connection_string: formData[CONNECTION_STRING_FIELD_NAME],
              container: formData[CONTAINER_FIELD_NAME]
            }
          : {})
      }
    };

    onSubmit(params);
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(submitHandler)} noValidate>
        <NameField isLoading={isGetDataLoading} />
        <ExportedDaysField isLoading={isGetDataLoading} />
        <FormLabel component="p">
          <FormattedMessage id="targetStorage" />
        </FormLabel>
        <Box mb={2}>
          <StorageTypeSelectorField isLoading={isGetDataLoading} isEdit={isEdit} />
        </Box>
        <Typography gutterBottom>
          <FormattedMessage id="targetStorageFormDescription" />
        </Typography>
        {storageType === BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT ? (
          <>
            <AwsAccessKeyIdField isLoading={isGetDataLoading} />
            <AwsSecretAccessKeyField isLoading={isGetDataLoading} />
            <BucketNameField isLoading={isGetDataLoading} />
            <S3PrefixField isLoading={isGetDataLoading} />
          </>
        ) : null}
        {storageType === BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT ? (
          <>
            <ConnectionStringField isLoading={isGetDataLoading} />
            <ContainerField isLoading={isGetDataLoading} />
          </>
        ) : null}
        <FormButtons isLoading={isSubmitLoading} onCancel={onCancel} isEdit={isEdit} />
      </form>
    </FormProvider>
  );
};

BIExportForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isEdit: PropTypes.bool,
  defaultValues: PropTypes.object,
  isLoadingProps: PropTypes.object
};

export default BIExportForm;
