import React from "react";
import PropTypes from "prop-types";
import IconButton from "components/IconButton";
import SubTitle from "components/SubTitle";
import TypographyLoader from "components/TypographyLoader";
import { isEmpty as isEmptyObject } from "utils/objects";

const SummaryList = ({ titleMessage, titleIconButton = {}, isLoading = false, items = [] }) => (
  <div>
    <div
      style={{
        display: "flex",
        alignItems: "center",
        height: "30px"
      }}
    >
      <SubTitle>{titleMessage}</SubTitle>
      {isEmptyObject(titleIconButton) ? null : <IconButton {...titleIconButton} />}
    </div>
    {isLoading ? <TypographyLoader linesCount={4} /> : <>{items}</>}
  </div>
);

SummaryList.propTypes = {
  titleMessage: PropTypes.node.isRequired,
  titleIconButton: PropTypes.object,
  isLoading: PropTypes.bool,
  items: PropTypes.node
};

export default SummaryList;
