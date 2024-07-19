### Summary

Hypertuning allows you to define a set of hyperparameters 
and automatically run your training code in parallel 
using a combination of hyperparameters on multiple 
cloud instances (only AWS is supported).

Use this page to create Runset Templates. 
Runset Template allows you to create predefined 
configurations for running hyperparameter tuning experiments. 
These templates can include various combinations of hyperparameters 
that you want to test.

### Requirements

```AmazonEC2FullAccess``` policy is required for 
the user specified on AWS data source connecting to use Hypertuning.

### Actions

- Update the Content: Click the Refresh button to view the latest information.

- Add a New Runset Template: Easily create a new runset template by clicking the green "Add" button.
   
  - Select Tasks: Select the tasks to which runset runs can be added.
  
  - Specify Infrastructure Settings: Specify clouds, acceptable instance types, and regions. 
  
  - Specify Maximum Runset Budget: Specify the maximum runset budget. When the budget is reached, training will be stopped and instances will be destroyed.

  - Define Hyperparameters: Specify training variables that will have different values for each runset run.

- Manage Runset Templates: Click on a table row to launch a new runset or view detailed information about a template, including comprehensive information on tasks, infrastructure, and hyperparameters. 

### Tips

- Automation: Simplifies the hyperparameter tuning process by automatically launching multiple experiments.

- Parallelization: Experiments can be executed in parallel on multiple instances, significantly speeding up the process.

- Performance Analysis: Analyze tuning results to understand the impact of different hyperparameters on training performance. Look for patterns and insights that can inform future tuning efforts and help in selecting more optimal ranges for hyperparameters.

- Experiment Against Your Training Code: Test your training code by including hyperparameters.