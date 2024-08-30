import { TextInput } from "components/forms/common/fields";
import InputLoader from "components/InputLoader";
import { getHyperparameterFieldName } from "../utils";

const HyperparameterField = ({ hyperparameters, isLoading = false }) =>
  isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <>
      {Object.entries(hyperparameters).map(([hyperparameterName, environmentVariableName]) => {
        const fieldName = getHyperparameterFieldName(environmentVariableName);

        return (
          <TextInput
            key={hyperparameterName}
            label={`${hyperparameterName} - ${environmentVariableName}`}
            required
            name={fieldName}
          />
        );
      })}
    </>
  );

export default HyperparameterField;
