import { useState } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import { createFilterOptions, Grid, Typography } from "@mui/material";
import Autocomplete from "@mui/material/Autocomplete";
import FormControl from "@mui/material/FormControl";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import Input from "components/Input";
import Selector from "components/Selector";
import { intl } from "translations/react-intl-config";
import { INSECURE_PORTS_MAP, MAX_PORT, MIN_PORT } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { isString, isWhitespaceString } from "utils/strings";
import { isNumberInRange, isWholeNumber } from "utils/validation";
import InsecurePortsTable from "./InsecurePortsTable";

const renderOption = (props, option) => {
  const [port, name] = option;
  return <li {...props}>{intl.formatMessage({ id: "value - value" }, { value1: name, value2: port })}</li>;
};

const portsMap = INSECURE_PORTS_MAP;

const filter = createFilterOptions({
  matchFrom: "any",
  stringify: (option) => `${option?.[0]} ${option?.[1]}`
});

const InsecurePorts = ({ insecurePorts = [], setData, isLoading, isChangeSettingsAllowed }) => {
  const [ruleParams, setRuleParams] = useState({
    selectedProtocol: "tcp",
    selectedPort: "",
    highlightedPort: "",
    portError: null
  });

  const onDelete = (protocol, port) => {
    setRuleParams({ ...ruleParams, portError: null });
    setData([...insecurePorts.filter((v) => v.protocol !== protocol || v.port !== port)]);
  };

  const validate = (port) => {
    const portNumber = Number(port);
    if (port === "") {
      return { message: intl.formatMessage({ id: "thisFieldIsRequired" }) };
    }
    if (isWhitespaceString(port)) {
      return { message: intl.formatMessage({ id: "notOnlyWhitespaces" }) };
    }
    if (isWholeNumber(portNumber)) {
      return { message: intl.formatMessage({ id: "wholeNumber" }) };
    }
    if (!isNumberInRange(portNumber, MIN_PORT, MAX_PORT)) {
      return { message: intl.formatMessage({ id: "portMustBeInRange" }, { minPort: MIN_PORT, maxPort: MAX_PORT }) };
    }
    if (insecurePorts.filter((v) => v.port === portNumber && v.protocol === ruleParams.selectedProtocol).length > 0) {
      return { message: intl.formatMessage({ id: "portAlreadyExists" }) };
    }
    return null;
  };

  const onAdd = () => {
    if (ruleParams.highlightedPort) {
      setRuleParams({ ...ruleParams, selectedPort: ruleParams.highlightedPort, highlightedPort: "" });
      return;
    }
    const portNumber = Number(ruleParams.selectedPort);
    const portError = validate(ruleParams.selectedPort);
    if (portError === null) {
      setData([
        ...insecurePorts,
        {
          protocol: ruleParams.selectedProtocol,
          port: portNumber
        }
      ]);
      setRuleParams({ ...ruleParams, selectedPort: "", highlightedPort: "" });
    } else {
      setRuleParams({ ...ruleParams, portError });
    }
  };

  const handleKeyDown = (e) => {
    if (e.keyCode === 13) {
      e.preventDefault();
      onAdd();
    }
  };

  return (
    <>
      <Grid container spacing={SPACING_1}>
        {isChangeSettingsAllowed && (
          <>
            <Grid item xs={3}>
              <Selector
                data={{
                  selected: ruleParams.selectedProtocol,
                  items: [
                    {
                      value: "tcp",
                      name: <FormattedMessage id="tcp" />
                    },
                    {
                      value: "udp",
                      name: <FormattedMessage id="udp" />
                    }
                  ]
                }}
                fullWidth
                required
                labelId="protocol"
                dataTestId="selector_protocol"
                onChange={(selectedProtocol) => setRuleParams({ ...ruleParams, selectedProtocol, portError: null })}
              />
            </Grid>
            <Grid item xs={6}>
              <Autocomplete
                freeSolo
                disableClearable
                clearOnEscape
                selectOnFocus
                value={ruleParams.selectedPort}
                options={Object.entries(portsMap)}
                getOptionLabel={(option) => (isString(option) ? option : option?.[0])}
                filterOptions={(options, params) => filter(options, params)}
                renderOption={renderOption}
                getOptionDisabled={(option) => insecurePorts.filter((v) => v.port === option?.[0]).length === 2}
                onInputChange={(event, selected, reason) => {
                  let port = selected;
                  if (reason === "selectOption") {
                    port = selected?.[0];
                  }
                  if (reason === "reset" && selected === "") {
                    setRuleParams({ ...ruleParams, selectedPort: port });
                  } else {
                    const portError = validate(port);
                    setRuleParams({ ...ruleParams, selectedPort: port, highlightedPort: "", portError });
                  }
                }}
                onHighlightChange={(event, selected) => {
                  const port = selected?.[0];
                  setRuleParams({ ...ruleParams, highlightedPort: port });
                }}
                renderInput={(params) => (
                  <Input
                    {...params}
                    error={ruleParams?.portError !== null}
                    helperText={ruleParams?.portError?.message}
                    dataTestId="selector_port"
                    label={<FormattedMessage id="port" />}
                    onKeyDown={handleKeyDown}
                    required
                  />
                )}
              />
            </Grid>
            <Grid item xs={3}>
              <FormControl fullWidth>
                <Button
                  dashedBorder
                  fullWidth
                  startIcon={<AddOutlinedIcon />}
                  messageId="addRule"
                  dataTestId="btn_add"
                  size="medium"
                  color="primary"
                  onClick={onAdd}
                />
              </FormControl>
            </Grid>
          </>
        )}
        <Grid item xs={12}>
          <Typography>
            <FormattedMessage
              id="allInboundsPortsNote"
              values={{
                strong: (chunks) => <strong>{chunks}</strong>
              }}
            />
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <InsecurePortsTable ports={insecurePorts} portsMap={portsMap} isLoading={isLoading} onDelete={onDelete} />
        </Grid>
      </Grid>
    </>
  );
};

export default InsecurePorts;
