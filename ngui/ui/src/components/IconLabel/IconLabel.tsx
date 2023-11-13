const IconLabel = ({ icon: startIcon, endIcon, label }) => (
  <div style={{ display: "inline-flex", verticalAlign: "middle", alignItems: "center" }}>
    {startIcon && <>{startIcon}&nbsp;</>}
    {label}
    {endIcon && <>&nbsp;{endIcon}</>}
  </div>
);

export default IconLabel;
