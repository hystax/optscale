import AssignmentRulesTable from "components/AssignmentRulesTable";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/AssignmentRulesTable`
};

const assignmentRules = [
  {
    active: true,
    name: "Rule 1",
    conditions: [
      {
        id: "1",
        meta_info: "A",
        type: "name_starts_with"
      }
    ]
  },
  {
    active: false,
    name: "Rule 2",
    conditions: [
      {
        id: "2",
        meta_info: "A",
        type: "name_starts_with"
      }
    ]
  },
  {
    active: true,
    name: "Rule 3",
    conditions: [
      {
        id: "1429f215",
        meta_info: "?",
        type: "name_ends_with"
      },
      {
        id: "2f3cd397",
        meta_info: "123!@#?",
        type: "name_is"
      },
      {
        id: "97291d6e",
        meta_info: "123",
        type: "name_starts_with"
      },
      {
        id: "f5a53732",
        meta_info: "!@#",
        type: "name_contains"
      }
    ]
  }
];

export const basic = () => <AssignmentRulesTable assignmentRules={assignmentRules} poolId="poolId" />;

export const empty = () => <AssignmentRulesTable assignmentRules={[]} poolId="poolId" />;
