module.exports = (containerName) => `import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { useApiState } from "hooks/useApiState";

const ${containerName} = () => {
  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(ACTION_TYPE);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(action());
    }
  }, [shouldInvoke, dispatch]);


  return (
    <div />
  );
};

${containerName}.propTypes = {
};

export default ${containerName};    
`;
