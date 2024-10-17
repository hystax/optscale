### **Summary**

Use this page to configure and launch runset.

### **View**

- Runset Configuration Form: Specify instance types, hyperparameters, abort conditions, and other runset properties.

### **Actions**

- Configure the Runset:

  - Select a Task: Choose the task to which runset runs can be added.
  
  - Specify Infrastructure Settings: Define the cloud, instance type, and region.
  
  - Define Hyperparameters: Enter a comma-separated list of hyperparameter values you want to try with this runset. For 
    each unique set of hyperparameters, an instance will be created in the cloud where the training code (run) will be 
    executed.
  
  - Enter Commands To Execute: Specify the commands that will be executed on each deployed instance. These can include 
    setup steps, data preprocessing tasks, task execution processes, or any other operations required for your ML runs.

  - Set Abort Conditions: Specify the conditions under which all infrastructure raised in the cloud will be 
    destroyed automatically.
  
    - Expenses Condition: Abort the runset when projected expenses exceed a specified limit.
    
    - Duration Condition: Abort an individual run if its duration exceeds a specified limit.
    
    - Goals Condition: Abort the runset when one of the runs reaches task goals.

- Launch Runset: Click the "Launch" button to initiate your hyperparameter tuning experiment.

### **Tips**

- Use Previous Configuration: Click the "Fill from latest launch" button to populate the fields with data from the 
  previous launch.
