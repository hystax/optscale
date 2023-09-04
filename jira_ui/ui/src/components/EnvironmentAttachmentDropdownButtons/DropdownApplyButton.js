import React from "react";
import { DropdownItem } from "@atlaskit/dropdown-menu";
import PropTypes from "prop-types";

const DropdownApplyButton = ({ text, onClick }) => <DropdownItem onClick={onClick}>{text}</DropdownItem>;

DropdownApplyButton.propTypes = {
  text: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired
};

export default DropdownApplyButton;
