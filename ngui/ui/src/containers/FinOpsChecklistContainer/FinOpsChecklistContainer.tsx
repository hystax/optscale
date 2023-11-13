import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getFinOpsChecklist, updateFinOpsChecklist } from "api";
import { GET_FINOPS_CHECKLIST, UPDATE_FINOPS_CHECKLIST } from "api/restapi/actionTypes";
import FinOpsChecklist from "components/FinOpsChecklist";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import sourceChecklist from "./checklist.json";

const FinOpsChecklistContainer = () => {
  const { organizationId } = useOrganizationInfo();

  const dispatch = useDispatch();

  const { isDataReady, shouldInvoke } = useApiState(GET_FINOPS_CHECKLIST, organizationId);
  const { isLoading: isUpdateLoading } = useApiState(UPDATE_FINOPS_CHECKLIST);

  const {
    apiData: { value: apiValue = "{}" }
  } = useApiData(GET_FINOPS_CHECKLIST);

  const { items: apiItems = [] } = JSON.parse(apiValue);
  const { items: sourceItems = [] } = sourceChecklist;

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getFinOpsChecklist(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  const update = (id) => {
    const idPositionInCheckedList = apiItems.indexOf(id);
    if (idPositionInCheckedList > -1) {
      apiItems.splice(idPositionInCheckedList, 1);
    } else {
      apiItems.push(id);
    }

    dispatch(updateFinOpsChecklist(organizationId, { items: apiItems }));
  };

  const addChecksToList = (whatIsChecked, list) =>
    list.map((item) => ({ ...item, checked: whatIsChecked.includes(item.id) })).filter((el) => !el.deleted);

  return (
    <FinOpsChecklist
      isLoading={!isDataReady || isUpdateLoading} // using isDataReady to prevent 0% blink before api request starts loading
      update={update}
      items={addChecksToList(apiItems, sourceItems)}
    />
  );
};

export default FinOpsChecklistContainer;
