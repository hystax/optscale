import Button from "components/Button";

const CancelButton = ({ navigateAway }) => <Button dataTestId="btn_cancel" messageId="cancel" onClick={navigateAway} />;

export default CancelButton;
