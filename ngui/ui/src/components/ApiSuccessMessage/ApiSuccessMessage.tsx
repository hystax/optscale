import ApiMessage from "components/ApiMessage";

const ApiSuccessMessage = ({ successCode, params }) => <ApiMessage code={successCode} params={params} />;

export default ApiSuccessMessage;
