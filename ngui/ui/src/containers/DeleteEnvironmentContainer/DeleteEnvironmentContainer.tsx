import { useDispatch } from "react-redux";
import { deleteEnvironment } from "api";
import { DELETE_ENVIRONMENT } from "api/restapi/actionTypes";
import DeleteEntity from "components/DeleteEntity";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const DeleteEnvironmentContainer = ({ id, name, onCancel }) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(DELETE_ENVIRONMENT);

  const onSubmit = () => {
    dispatch((_, getState) => {
      dispatch(deleteEnvironment(id))
        .then(() => {
          if (isError(DELETE_ENVIRONMENT, getState())) {
            return Promise.reject();
          }
          return Promise.resolve();
        })
        .then(onCancel);
    });
  };

  return (
    <DeleteEntity
      onDelete={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      deleteButtonProps={{
        onDelete: onSubmit
      }}
      dataTestIds={{
        text: "p_delete",
        deleteButton: "btn_smodal_delete",
        cancelButton: "btn_cancel"
      }}
      message={{
        messageId: "deleteEnvironmentQuestion",
        values: {
          name
        }
      }}
    />
  );
};

export default DeleteEnvironmentContainer;
