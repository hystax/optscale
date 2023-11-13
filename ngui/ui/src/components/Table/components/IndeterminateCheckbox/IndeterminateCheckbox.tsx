import { useRef, useEffect, forwardRef } from "react";
import Checkbox from "@mui/material/Checkbox";

// checkbox component for select column
// * forwardRef is used by official examples, so sticking to it for now
// * deconstructing "title" to avoid passing it's default value into checkbox
const IndeterminateCheckbox = forwardRef(({ indeterminate, title, id, ...rest }, ref) => {
  const defaultRef = useRef();
  const resolvedRef = ref || defaultRef;

  useEffect(() => {
    resolvedRef.current.indeterminate = indeterminate;
  }, [resolvedRef, indeterminate]);

  return <Checkbox data-test-id={`selection_${id}`} ref={resolvedRef} indeterminate={indeterminate} {...rest} />;
});

export default IndeterminateCheckbox;
