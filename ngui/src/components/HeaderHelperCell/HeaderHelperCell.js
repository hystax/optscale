import React from "react";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import QuestionMark from "components/QuestionMark";

const HeaderHelperCell = ({ title, titleMessageId, titleDataTestId, helperMessageId, helperMessageValues }) => {
  const intl = useIntl();

  return (
    <Box width="max-content" display="flex" alignItems="center">
      <span data-test-id={titleDataTestId}>{title ?? intl.formatMessage({ id: titleMessageId })}</span>
      <QuestionMark messageId={helperMessageId} messageValues={helperMessageValues} fontSize="small" />
    </Box>
  );
};

HeaderHelperCell.propTypes = {
  title: PropTypes.node,
  titleMessageId: PropTypes.string,
  helperMessageId: PropTypes.string.isRequired,
  helperMessageValues: PropTypes.object,
  titleDataTestId: PropTypes.string
};

export default HeaderHelperCell;
