import { FormattedMessage } from "react-intl";
import CircleLabel from "components/CircleLabel";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import KeyValueLabel from "components/KeyValueLabel";
import SlicedText from "components/SlicedText";
import { useGoalMetColors } from "hooks/useGoalMetColors";

const MAX_GOAL_NAME_LENGTH = 40;

const GoalLabel = ({ name, goalValue, targetGoalValue, reached }) => {
  const { goalMet: goalMetColor, goalNotMet: goalNotMetColor } = useGoalMetColors();

  return (
    <KeyValueLabel
      text={<SlicedText limit={MAX_GOAL_NAME_LENGTH} text={name} />}
      value={
        goalValue !== undefined ? (
          <span style={{ whiteSpace: "nowrap" }}>
            <CircleLabel
              figureColor={reached ? goalMetColor : goalNotMetColor}
              label={
                <FormattedMessage
                  id="value / value"
                  values={{
                    value1: <DynamicFractionDigitsValue value={goalValue} />,
                    value2: <DynamicFractionDigitsValue value={targetGoalValue} />
                  }}
                />
              }
              tooltip={{ show: true, messageId: reached ? "goalMet" : "goalNotMet" }}
              textFirst={false}
            />
          </span>
        ) : undefined
      }
    />
  );
};

export default GoalLabel;
