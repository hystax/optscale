import ApiMessage from "components/ApiMessage";

const ApiErrorMessage = ({ errorCode, reason, url, params = [] }) => (
  <ApiMessage defaultMessage={`${url}: ${reason}`} code={errorCode} params={params} />
);

export default ApiErrorMessage;
