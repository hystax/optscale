import FormattedMoney from "components/FormattedMoney";
import TextWithDataTestId from "components/TextWithDataTestId";

const ExpenseMessage = ({ type, limit }) => (
  <TextWithDataTestId dataTestId={`p_${type}_value`}>
    <FormattedMoney value={limit} />
  </TextWithDataTestId>
);

export default ExpenseMessage;
