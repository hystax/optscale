import { useState, useRef } from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import SearchOutlinedIcon from "@mui/icons-material/SearchOutlined";
import { useIntl } from "react-intl";
import IconButton from "components/IconButton";
import Input from "components/Input";
import useStyles from "./SearchInput.styles";

type SearchInputProps = {
  onSearch: (text: string) => void;
  initialSearchText?: string;
  dataTestIds?: {
    searchInput?: string;
    searchButton?: string;
    deleteSearchButton?: string;
  };
  sx?: Record<string, unknown>;
  fullWidth?: boolean;
};

const SearchInput = ({ onSearch, initialSearchText = "", dataTestIds = {}, sx = {}, fullWidth = false }: SearchInputProps) => {
  const { classes } = useStyles();
  const intl = useIntl();
  const inputRef = useRef();

  const {
    searchInput: searchInputDataTestId,
    searchButton: searchButtonDataTestId,
    deleteSearchButton: deleteSearchButtonDataTestId
  } = dataTestIds;

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
      fullWidth={fullWidth}
      placeholder={intl.formatMessage({ id: "search" })}
      InputProps={{
        startAdornment: (
          <IconButton
            dataTestId={searchButtonDataTestId}
            icon={<SearchOutlinedIcon />}
            onClick={() => {
              inputRef.current.focus();
              onSearchHandler();
            }}
          />
        ),
        endAdornment: currentText !== "" && (
          <IconButton
            dataTestId={deleteSearchButtonDataTestId}
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
      value={currentText}
      onChange={handleInputChange}
      onKeyDown={handleKeyDown}
      dataTestId={searchInputDataTestId}
      sx={sx}
    />
  );
};

export default SearchInput;
