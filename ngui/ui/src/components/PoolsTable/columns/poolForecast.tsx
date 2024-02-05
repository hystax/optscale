import PoolForecast from "components/PoolForecast";
import TextWithDataTestId from "components/TextWithDataTestId";

const poolForecast = ({ defaultSort } = {}) => ({
  header: <TextWithDataTestId dataTestId="lbl_forecast" messageId="forecastThisMonth" />,
  accessorKey: "forecast",
  cell: ({
    cell,
    row: {
      original: { limit = 0 }
    }
  }) => <PoolForecast limit={limit} forecast={cell.getValue()} />,
  defaultSort,
  columnSelector: {
    accessor: "forecast",
    messageId: "forecast",
    dataTestId: "btn_toggle_forecast"
  }
});

export default poolForecast;
