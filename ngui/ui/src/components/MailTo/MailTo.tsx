import Link from "@mui/material/Link";

const MailTo = ({ email, text, dataTestId }) => (
  <Link data-test-id={dataTestId} href={`mailto:${email}`} rel="noopener">
    {text}
  </Link>
);

export default MailTo;
