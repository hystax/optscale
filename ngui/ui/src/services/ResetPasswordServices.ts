import { useDispatch } from "react-redux";
import { restorePassword } from "api";
import { RESTORE_PASSWORD } from "api/restapi/actionTypes";
import { useCreateTokenMutation, useUpdateUserMutation } from "graphql/__generated__/hooks/auth";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const useSendVerificationCode = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(RESTORE_PASSWORD);

  const onSend = (email: string, linkParams: Record<string, string | undefined>) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(restorePassword({ email, linkParams })).then(() => {
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
  const [createToken, { loading: loginLoading }] = useCreateTokenMutation();

  const onGet = (email: string, code: string) =>
    createToken({ variables: { email, code } }).then(({ data: { token } }) => Promise.resolve(token));

  return { onGet, isLoading: loginLoading };
};

const useUpdateUserPassword = () => {
  const [updateUser, { loading: updateUserLoading }] = useUpdateUserMutation();

  const onUpdate = (
    token: {
      user_id: string;
      user_email: string;
      token: string;
    },
    newPassword: string
  ) =>
    updateUser({
      variables: {
        id: token.user_id,
        params: { password: newPassword },
      },
      context: {
        headers: {
          "x-optscale-token": token.token,
        },
      },
    });

  return { onUpdate, isLoading: updateUserLoading };
};

const useGetNewToken = () => {
  const [createToken, { loading: loginLoading }] = useCreateTokenMutation();

  const onGet = (email: string, password: string) =>
    createToken({ variables: { email, password } }).then(({ data: { token } }) => Promise.resolve(token));

  return { onGet, isLoading: loginLoading };
};

function ResetPasswordServices() {
  return { useSendVerificationCode, useGetVerificationCodeToken, useUpdateUserPassword, useGetNewToken };
}

export default ResetPasswordServices;
