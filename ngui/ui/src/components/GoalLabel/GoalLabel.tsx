import { FormattedMessage } from "react-intl";
import CircleLabel from "components/CircleLabel";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import MetricUnitLabel from "components/MetricUnitLabel";
import SlicedText from "components/SlicedText";
import { useGoalMetColors } from "hooks/useGoalMetColors";

const MAX_GOAL_NAME_LENGTH = 40;

type GoalLabelProps = {
  name: string;
  reached?: boolean;
  unit?: string;
  goalValue?: number;
  targetGoalValue?: number;
  displayInOneLine?: boolean;
};

const GoalLabel = ({ name, goalValue, targetGoalValue, reached, unit, displayInOneLine = false }: GoalLabelProps) => {
  const { goalMet: goalMetColor, goalNotMet: goalNotMetColor } = useGoalMetColors();

  const renderValue = () => {
    if (goalValue === undefined || targetGoalValue === undefined) {
      return "-";
    }

    return (
      <CircleLabel
        figureColor={reached ? goalMetColor : goalNotMetColor}
        label={
          <strong style={{ whiteSpace: "nowrap" }}>
            <FormattedMessage
              id="value / value"
              values={{
                value1: <DynamicFractionDigitsValue value={goalValue} />,
                value2: <DynamicFractionDigitsValue value={targetGoalValue} />,
              }}
            />
          </strong>
        }
        tooltip={{ show: true, messageId: reached ? "goalMet" : "goalNotMet" }}
        textFirst={false}
      />
    );
  };

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        ...(displayInOneLine ? { flexWrap: "nowrap", whiteSpace: "nowrap" } : { flexWrap: "wrap" }),
      }}
    >
      <span>
        <MetricUnitLabel label={<SlicedText limit={MAX_GOAL_NAME_LENGTH} text={name} />} unit={unit} showUnitInParentheses />
        :&nbsp;
      </span>
      <span>{renderValue()}</span>
    </div>
  );
};

export default GoalLabel;
