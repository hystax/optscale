import React from "react";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import IconButton from "components/IconButton";
import Input from "components/Input";
import { NAME_MAX_SIZE } from "utils/constants";

const FIELD_NAME = "name";

const EditOrganizationConstraintNameForm = ({ defaultName, onCancel, onSubmit, isLoading }) => {
  const intl = useIntl();

  const {
    register,
    formState: { errors },
    handleSubmit
  } = useForm({
    defaultValues: {
      [FIELD_NAME]: defaultName
    }
  });

  return (
    <form noValidate onSubmit={handleSubmit((formData) => onSubmit(formData[FIELD_NAME]))}>
      <Box
        sx={{
          display: "flex",
          width: {
            xs: "inherit",
            md: "50%"
          }
        }}
      >
        <Input
          label={<FormattedMessage id="name" />}
          required
          dataTestId={`input_${FIELD_NAME}`}
          error={!!errors[FIELD_NAME]}
          helperText={errors[FIELD_NAME]?.message}
          sx={{
            marginRight: (theme) => theme.spacing(1)
          }}
          {...register(FIELD_NAME, {
            required: {
              value: true,
              message: intl.formatMessage({ id: "thisFieldIsRequired" })
            },
            maxLength: {
              value: NAME_MAX_SIZE,
              message: intl.formatMessage(
                { id: "maxLength" },
                { inputName: intl.formatMessage({ id: "value" }), max: NAME_MAX_SIZE }
              )
            }
          })}
        />
        <FormButtonsWrapper mt={0} mb={0} alignItems="center">
          <IconButton icon={<CheckOutlinedIcon />} type="submit" isLoading={isLoading} />
          <IconButton key="edit" icon={<CloseIcon />} onClick={onCancel} />
        </FormButtonsWrapper>
      </Box>
    </form>
  );
};

EditOrganizationConstraintNameForm.propTypes = {
  defaultName: PropTypes.string.isRequired,
  onCancel: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default EditOrganizationConstraintNameForm;
