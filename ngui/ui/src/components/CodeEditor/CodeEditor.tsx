import { forwardRef } from "react";
import { useTheme } from "@mui/material/styles";
import UiwCodeEditor from "@uiw/react-textarea-code-editor";

const CodeEditor = forwardRef(
  ({ value, placeholder, className, language, onChange, onBlur, style, readOnly = false, ...rest }, ref) => {
    const theme = useTheme();

    return (
      <UiwCodeEditor
        ref={ref}
        value={value}
        padding={10}
        language={language}
        placeholder={placeholder}
        className={className}
        onChange={(e) => onChange(e.target.value)}
        style={{
          fontSize: 14,
          fontFamily: theme.typography.mono.fontFamily,
          borderRadius: "4px",
          ...style
        }}
        readOnly={readOnly}
        data-color-mode="light"
        {...rest}
      />
    );
  }
);

export default CodeEditor;
