import { useDispatch } from "react-redux";
import { restorePassword, getToken, updateUser } from "api";
import { GET_TOKEN, UPDATE_USER } from "api/auth/actionTypes";
import { RESTORE_PASSWORD } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const useSendVerificationCode = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(RESTORE_PASSWORD);

  const onSend = (email: string) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(restorePassword(email)).then(() => {
          if (!isError(RESTORE_PASSWORD, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onSend, isLoading };
};

const useGetVerificationCodeToken = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(GET_TOKEN);

  const onGet = (email: string, code: string) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(
          getToken({
            email,
            code
          })
        ).then(() => {
          if (!isError(GET_TOKEN, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onGet, isLoading };
};

const useUpdateUserPassword = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_USER);

  const {
    apiData: { userId }
  } = useApiData(GET_TOKEN);

  const onUpdate = (newPassword: string) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(
          updateUser(userId, {
            password: newPassword
          })
        ).then(() => {
          if (!isError(UPDATE_USER, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useGetNewToken = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(GET_TOKEN);

  const onGet = (email: string, password: string) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(getToken({ email, password })).then(() => {
          if (!isError(GET_TOKEN, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onGet, isLoading };
};

function ResetPasswordServices() {
  return { useSendVerificationCode, useGetVerificationCodeToken, useUpdateUserPassword, useGetNewToken };
}

export default ResetPasswordServices;
