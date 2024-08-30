import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import { Box } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import IconButton from "components/IconButton";
import { FIELD_NAMES } from "./constants";
import { NameField } from "./FormElements";
import { EditOrganizationConstraintNameFormProps, FormValues } from "./types";

const EditOrganizationConstraintNameForm = ({
  defaultName,
  onCancel,
  onSubmit,
  isLoading = false
}: EditOrganizationConstraintNameFormProps) => {
  const methods = useForm<FormValues>({
    defaultValues: {
      [FIELD_NAMES.NAME]: defaultName
    }
  });

  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form noValidate onSubmit={handleSubmit(onSubmit)}>
        <Box
          sx={{
            display: "flex",
            width: {
              xs: "inherit",
              md: "50%"
            }
          }}
        >
          <NameField />
          <FormButtonsWrapper mt={0} mb={0} alignItems="center">
            <IconButton icon={<CheckOutlinedIcon />} type="submit" isLoading={isLoading} />
            <IconButton key="edit" icon={<CloseIcon />} onClick={onCancel} />
          </FormButtonsWrapper>
        </Box>
      </form>
    </FormProvider>
  );
};

export default EditOrganizationConstraintNameForm;
