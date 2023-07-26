import React, { useState, useRef } from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import SearchOutlinedIcon from "@mui/icons-material/SearchOutlined";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import IconButton from "components/IconButton";
import Input from "components/Input";
import useStyles from "./SearchInput.styles";

const SearchInput = ({ onSearch, initialSearchText = "", dataTestIds = {}, sx = {} }) => {
  const { classes, cx } = useStyles();
  const intl = useIntl();
  const inputRef = useRef();

  const { searchInput = null, searchButton = null, deleteSearchButton = null } = dataTestIds;

  const [currentText, setCurrentText] = useState(initialSearchText);

  const handleInputChange = (e) => {
    setCurrentText(e.target.value);
  };

  const onSearchHandler = (text = currentText) => {
    onSearch(text);
  };

  const onSearchClear = () => {
    setCurrentText("");
    onSearchHandler(""); // here is a trick — current text state won't be updated, so simply sending empty string manually
  };

  const handleKeyDown = (e) => {
    if (e.keyCode === 13) {
      onSearchHandler();
      e.preventDefault();
    }
  };

  return (
    <Input
      fullWidth={false}
      placeholder={intl.formatMessage({ id: "search" })}
      InputProps={{
        startAdornment: (
          <IconButton
            dataTestId={searchButton}
            icon={<SearchOutlinedIcon />}
            onClick={() => {
              inputRef.current.focus();
              onSearchHandler();
            }}
          />
        ),
        endAdornment: currentText !== "" && (
          <IconButton
            dataTestId={deleteSearchButton}
            icon={<CancelIcon className={classes.clearSearchIcon} />}
            onClick={() => {
              inputRef.current.focus();
              onSearchClear();
            }}
          />
        ),
        sx: { paddingLeft: 0 }
      }}
      ref={inputRef}
      margin="none"
      className={cx(classes.input)}
      value={currentText}
      onChange={handleInputChange}
      onKeyDown={handleKeyDown}
      dataTestId={searchInput}
      sx={sx}
    />
  );
};

SearchInput.propTypes = {
  onSearch: PropTypes.func,
  initialSearchText: PropTypes.string,
  dataTestIds: PropTypes.shape({
    searchInput: PropTypes.string,
    searchButton: PropTypes.string,
    deleteSearchButton: PropTypes.string
  }),
  sx: PropTypes.object
};

export default SearchInput;
