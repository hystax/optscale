import Button from "components/Button";
import IconError from "components/IconError";

export default {
  component: IconError
};

export const basic = () => <IconError messageId="hystax" />;

export const withButton = () => (
  <IconError messageId="hystax">
    <Button color="primary" messageId="hystax" size="large" />
  </IconError>
);
