import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";

const InfoArea = ({
  invalidPageQuery = false,
  showCounters,
  hideTotal,
  hideDisplayed,
  totalNumber = 0,
  rowsLength = 0,
  pagesNum = 0,
  pageSize = 0,
  currentPage = 0,
  selectedRowsCount = 0,
  dataTestIds = {}
}) => {
  const getDisplayedValue = () => {
    // check if there is no pagination or pages count is more than 1 page
    if (pageSize === 0 || pagesNum <= 1) {
      // "Displayed: rowsLen" when there's no paging involved
      return rowsLength;
    }

    // "Displayed: from firstRowOnPageIndex to lastRowOnPageIndex"
    const from = currentPage * pageSize + 1;
    const currentPageLastRowIndex = (currentPage + 1) * pageSize;
    const to = Math.min(currentPageLastRowIndex, rowsLength);
    return <FormattedMessage id="fromTo" values={{ from, to }} />;
  };

  return (
    showCounters && (
      <>
        {!hideTotal && (
          <KeyValueLabel
            value={totalNumber}
            messageId="total"
            dataTestIds={{ typography: dataTestIds.total, key: dataTestIds.totalKey, value: dataTestIds.totalValue }}
          />
        )}
        {!hideDisplayed && !invalidPageQuery && (
          <KeyValueLabel
            value={getDisplayedValue()}
            messageId="displayed"
            dataTestIds={{
              typography: dataTestIds.displayed,
              key: dataTestIds.displayedKey,
              value: dataTestIds.displayedValue
            }}
          />
        )}
        {selectedRowsCount !== 0 && (
          <KeyValueLabel
            value={selectedRowsCount}
            messageId="selected"
            dataTestIds={{ typography: dataTestIds.selected, key: dataTestIds.selectedKey, value: dataTestIds.selectedValue }}
          />
        )}
      </>
    )
  );
};

export const InfoAreaTestIdsProp = PropTypes.shape({
  total: PropTypes.string,
  displayed: PropTypes.string,
  selected: PropTypes.string
});

export const InfoAreaProps = {
  invalidPageQuery: PropTypes.bool,
  showCounters: PropTypes.bool.isRequired,
  hideTotal: PropTypes.bool,
  hideDisplayed: PropTypes.bool,
  totalNumber: PropTypes.number,
  rowsLength: PropTypes.number, // todo: maybe rename, not obv
  pagesNum: PropTypes.number,
  pageSize: PropTypes.number,
  currentPage: PropTypes.number,
  selectedRowsCount: PropTypes.number,
  dataTestIds: InfoAreaTestIdsProp
};

InfoArea.propTypes = InfoAreaProps;

export default InfoArea;
