import { useFormContext, Controller } from "react-hook-form";
import { MB } from "utils/constants";
import Dropzone from "./Dropzone";
import { isAcceptedFile } from "./utils";

const FIELD_NAME = "upload";

const DropzoneArea = ({ acceptedFiles, name = FIELD_NAME, maxFileSizeMb = 512 }) => {
  const {
    control,
    formState: { errors },
    trigger,
    clearErrors,
  } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      rules={{
        required: {
          value: true,
          message: "selectFileToUpload",
        },
        validate: {
          type: (value) => (!isAcceptedFile(value, acceptedFiles) ? "fileTypeNotSupported" : true),
          size: (value) => (value.size > maxFileSizeMb * MB ? "fileIsTooBig" : true),
        },
      }}
      render={({ field: { onChange } }) => (
        <Dropzone
          acceptedFiles={acceptedFiles}
          errorMessageId={errors[name] && errors[name].message}
          onChange={(file) => {
            onChange(file);
            if (file) {
              trigger(name);
            } else {
              clearErrors(name);
            }
          }}
        />
      )}
    />
  );
};

export default DropzoneArea;
