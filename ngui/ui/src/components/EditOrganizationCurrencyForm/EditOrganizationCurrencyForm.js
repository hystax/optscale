import React from "react";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { useForm, FormProvider } from "react-hook-form";
import IconButton from "components/IconButton";
import { OrganizationCurrencyField, CURRENCY_FIELD_NAME } from "./Fields";

const EditOrganizationCurrencyForm = ({ defaultCurrency, onSubmit, onCancel, isLoading = false }) => {
  const methods = useForm({
    defaultValues: {
      [CURRENCY_FIELD_NAME]: defaultCurrency
    }
  });
  const { handleSubmit } = methods;

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((formData) => {
          onSubmit(formData[CURRENCY_FIELD_NAME]);
        })}
        noValidate
      >
        <Box display="flex">
          <Box>
            <OrganizationCurrencyField />
          </Box>
          <Box display="flex" height="max-content">
            <IconButton isLoading={isLoading} icon={<CheckOutlinedIcon />} type="submit" />
            <IconButton icon={<CloseIcon />} onClick={onCancel} />
          </Box>
        </Box>
      </form>
    </FormProvider>
  );
};

EditOrganizationCurrencyForm.propTypes = {
  defaultCurrency: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default EditOrganizationCurrencyForm;
