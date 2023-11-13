import ErrorComponent from "components/Error";
import PageContentWrapper from "components/PageContentWrapper";

const Error = ({ context }) => (
  <PageContentWrapper>
    <ErrorComponent messageId={context.messageId} />
  </PageContentWrapper>
);

export default Error;
