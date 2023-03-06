import React, { useEffect } from "react";
import FormHelperText from "@mui/material/FormHelperText";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import { useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import Filters from "components/Filters";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import Input from "components/Input";
import ResourcesPerspectiveValuesDescription from "components/ResourcesPerspectiveValuesDescription";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { notOnlyWhiteSpaces, validatePerspectiveSchema } from "utils/validation";

const PERSPECTIVE_NAME_FIELD_NAME = "name";
const PERSPECTIVE_PAYLOAD_FIELD_NAME = "payload";

const CreateResourcePerspectiveForm = ({ onSubmit, breakdownBy, breakdownData, filters, isLoading = false, onCancel }) => {
  const {
    register,
    unregister,
    handleSubmit,
    formState: { errors }
  } = useForm({
    defaultValues: {
      name: "",
      payload: {
        filters: {
          filterValues: filters.getFilterValuesForAppliedFilters(),
          appliedFilters: filters.getAppliedFilters()
        },
        breakdownBy,
        breakdownData
      }
    }
  });

  const intl = useIntl();

  useEffect(() => {
    register(PERSPECTIVE_PAYLOAD_FIELD_NAME, {
      validate: {
        isFormatValid: (data) => {
          const [isValid] = validatePerspectiveSchema(data);

          return isValid ? true : intl.formatMessage({ id: "incorrectDataFormat" });
        }
      }
    });

    return () => unregister(PERSPECTIVE_PAYLOAD_FIELD_NAME);
  }, [intl, register, unregister]);

  return (
    <form noValidate onSubmit={handleSubmit(onSubmit)}>
      <Input
        label={intl.formatMessage({ id: "name" })}
        required
        error={!!errors?.[PERSPECTIVE_NAME_FIELD_NAME]}
        helperText={errors?.[PERSPECTIVE_NAME_FIELD_NAME]?.message}
        {...register(PERSPECTIVE_NAME_FIELD_NAME, {
          required: {
            value: true,
            message: intl.formatMessage({ id: "thisFieldIsRequired" })
          },
          maxLength: {
            value: DEFAULT_MAX_INPUT_LENGTH,
            message: intl.formatMessage(
              { id: "maxLength" },
              { inputName: intl.formatMessage({ id: "name" }), max: DEFAULT_MAX_INPUT_LENGTH }
            )
          },
          validate: {
            notOnlyWhiteSpaces
          }
        })}
      />
      <ResourcesPerspectiveValuesDescription
        breakdownBy={breakdownBy}
        breakdownData={breakdownData}
        filters={filters.getAppliedValues()}
      />
      {errors?.[PERSPECTIVE_PAYLOAD_FIELD_NAME]?.message && (
        <FormHelperText error>{errors?.[PERSPECTIVE_PAYLOAD_FIELD_NAME]?.message}</FormHelperText>
      )}
      <FormButtonsWrapper>
        <ButtonLoader
          isLoading={isLoading}
          variant="contained"
          color="primary"
          messageId="save"
          type="submit"
          loaderDataTestId="loading_btn_save"
          dataTestId="btn_save"
        />
        <Button messageId="cancel" onClick={onCancel} dataTestId="btn_cancel" />
      </FormButtonsWrapper>
    </form>
  );
};

CreateResourcePerspectiveForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  breakdownBy: PropTypes.string.isRequired,
  breakdownData: PropTypes.object.isRequired,
  filters: PropTypes.instanceOf(Filters).isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default CreateResourcePerspectiveForm;
