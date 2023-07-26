import React from "react";
import PropTypes from "prop-types";
import ErrorComponent from "components/Error";
import PageContentWrapper from "components/PageContentWrapper";

const Error = ({ context }) => (
  <PageContentWrapper>
    <ErrorComponent messageId={context.messageId} />
  </PageContentWrapper>
);

Error.propTypes = {
  context: PropTypes.object.isRequired
};

export default Error;
