import React from "react";
import CheckOutlinedIcon from "@mui/icons-material/CheckOutlined";
import CloseIcon from "@mui/icons-material/Close";
import PropTypes from "prop-types";
import { useForm } from "react-hook-form";
import { useIntl } from "react-intl";
import EnvironmentPropertyNameInput from "components/EnvironmentPropertyNameInput";
import EnvironmentPropertyValueInput from "components/EnvironmentPropertyValueInput";
import IconButton from "components/IconButton";
import PropertyLayout from "components/PropertyLayout";

const PROPERTY_NAME = "propertyName";
const PROPERTY_VALUE = "propertyValue";

const EnvironmentPropertyForm = ({
  defaultPropertyName,
  defaultPropertyValue,
  onSubmit,
  onCancel,
  isLoading,
  isEdit,
  existingProperties
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm({
    defaultValues: {
      propertyName: defaultPropertyName,
      propertyValue: defaultPropertyValue
    }
  });

  const intl = useIntl();

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <PropertyLayout
        propertyName={
          <EnvironmentPropertyNameInput
            name={PROPERTY_NAME}
            register={register}
            error={!!errors[PROPERTY_NAME]}
            helperText={errors[PROPERTY_NAME] && errors[PROPERTY_NAME].message}
            readOnly={isEdit}
            validate={{
              unique: (value) => {
                const propertyAlreadyExists = Object.keys(existingProperties).some(
                  (existingPropertyName) => defaultPropertyName !== existingPropertyName && value === existingPropertyName
                );

                return !propertyAlreadyExists || intl.formatMessage({ id: "propertyNamesShouldBeUnique" });
              }
            }}
          />
        }
        propertyValue={
          <EnvironmentPropertyValueInput
            name={PROPERTY_VALUE}
            register={register}
            error={!!errors[PROPERTY_VALUE]}
            helperText={errors[PROPERTY_VALUE] && errors[PROPERTY_VALUE].message}
          />
        }
        iconButtons={
          <>
            <IconButton icon={<CheckOutlinedIcon />} type="submit" isLoading={isLoading} />
            <IconButton icon={<CloseIcon />} onClick={onCancel} />
          </>
        }
      />
    </form>
  );
};

EnvironmentPropertyForm.propTypes = {
  defaultPropertyName: PropTypes.string.isRequired,
  defaultPropertyValue: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  isEdit: PropTypes.bool,
  existingProperties: PropTypes.object
};

export default EnvironmentPropertyForm;
