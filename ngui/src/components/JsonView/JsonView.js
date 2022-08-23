import React from "react";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import JSONInput from "react-json-editor-ajrm";
import locale from "react-json-editor-ajrm/locale/en";

const JsonView = ({ value, onChange, id, viewOnly = false }) => {
  const theme = useTheme();

  return (
    <JSONInput
      id={id}
      locale={locale}
      placeholder={value}
      height="auto"
      width="100%"
      onChange={onChange}
      waitAfterKeyPress={0}
      confirmGood={false}
      colors={theme.palette.json}
      viewOnly={viewOnly}
      style={{
        warningBox: { display: "none" },
        body: { fontSize: theme.typography.pxToRem(14), fontFamily: "monospace" }
      }}
    />
  );
};

JsonView.propTypes = {
  value: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  id: PropTypes.string,
  viewOnly: PropTypes.bool
};

export default JsonView;
