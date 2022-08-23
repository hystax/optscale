import { GET_TOKEN, SET_TOKEN } from "./actionTypes";

export const onSuccessSignIn = (data) => ({
  type: SET_TOKEN,
  payload: data,
  label: GET_TOKEN
});

export const onSuccessCreateUser = ({ id, token, email }) => ({
  type: SET_TOKEN,
  payload: {
    user_id: id,
    token,
    user_email: email
  },
  label: GET_TOKEN
});
