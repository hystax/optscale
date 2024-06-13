import { useEffect } from "react";
import { Box, FormLabel, Typography } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { BI_EXPORT_STORAGE_TYPE } from "utils/biExport";
import { FIELD_NAMES } from "./constants";
import {
  StorageTypeSelectorField,
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
import { BIExportFormProps, ExportType, FormValues } from "./types";

const BIExportForm = ({ defaultValues, isLoadingProps, onSubmit, onCancel, isEdit = false }: BIExportFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues
  });

  const { isSubmitLoading, isGetDataLoading } = isLoadingProps;

  const { handleSubmit, reset, watch } = methods;

  const storageType = watch(FIELD_NAMES.STORAGE_TYPE);

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...defaultValues
    }));
  }, [defaultValues, reset]);

  const submitHandler = (formData: FormValues) => {
    const getMeta = (): ExportType => {
      const type = formData[FIELD_NAMES.STORAGE_TYPE];

      switch (type) {
        case BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT:
          return {
            type,
            meta: {
              access_key_id: formData[FIELD_NAMES.AWS_STORAGE.AWS_ACCESS_KEY_ID_FIELD_NAME],
              secret_access_key: formData[FIELD_NAMES.AWS_STORAGE.AWS_SECRET_ACCESS_KEY_FIELD_NAME],
              bucket: formData[FIELD_NAMES.AWS_STORAGE.BUCKET_NAME_FIELD_NAME],
              s3_prefix: formData[FIELD_NAMES.AWS_STORAGE.S3_PATH_FIELD_NAME] || undefined
            }
          };
        case BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT:
          return {
            type,
            meta: {
              connection_string: formData[FIELD_NAMES.AZURE_STORAGE.CONNECTION_STRING_FIELD_NAME],
              container: formData[FIELD_NAMES.AZURE_STORAGE.CONTAINER_FIELD_NAME]
            }
          };
        default: {
          const exhaustiveCheck: never = type;
          throw new Error(`Unhandled export type case ${exhaustiveCheck}`);
        }
      }
    };

    const { type, meta } = getMeta();

    onSubmit({
      name: formData[FIELD_NAMES.NAME],
      days: Number(formData[FIELD_NAMES.EXPORTED_DAYS]),
      meta,
      type: isEdit ? undefined : type
    });
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

export default BIExportForm;
