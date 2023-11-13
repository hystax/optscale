import { useForm, FormProvider } from "react-hook-form";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import DropzoneArea from "./DropzoneArea";

const FIELD_NAME = "upload";

const DropzoneForm = ({ onUpload, acceptedFiles, isLoading, maxFileSizeMb = 512 }) => {
  const methods = useForm();

  const { handleSubmit } = methods;

  const onSubmit = ({ [FIELD_NAME]: file }) => {
    onUpload(file);
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <DropzoneArea acceptedFiles={acceptedFiles} maxFileSizeMb={maxFileSizeMb} />
        <FormButtonsWrapper>
          <ButtonLoader messageId="upload" color="primary" variant="contained" type="submit" isLoading={isLoading} />
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

export default DropzoneForm;
