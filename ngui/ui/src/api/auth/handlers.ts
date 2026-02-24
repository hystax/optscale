import { GET_TOKEN, SET_TOKEN } from "./actionTypes";

export const onSuccessSignIn = (data) => ({
  type: SET_TOKEN,
  payload: data,
  label: GET_TOKEN,
});
