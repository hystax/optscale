import React from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import { useForm, FormProvider } from "react-hook-form";
import TestProvider from "tests/TestProvider";
import RangePickerFormField from "./RangePickerFormField";

const WrapWithFormProvider = (props) => {
  const methods = useForm();
  return <FormProvider {...methods}>{props.children}</FormProvider>;
};

WrapWithFormProvider.propTypes = {
  children: PropTypes.node.isRequired
};

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <WrapWithFormProvider>
        <RangePickerFormField startDatePickerName="startDatePickerName" endDatePickerName="endDatePickerName" />
      </WrapWithFormProvider>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
