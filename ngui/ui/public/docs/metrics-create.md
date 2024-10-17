### **Summary**

Metrics help assess how well the training code makes predictions compared to the actual outcomes. They can vary 
depending on the type of task being solved (e.g., classification, regression).

Use this page to create a new metric.  

### **View**

- Add Metric Form: Specify name, key, tendency, and other metric properties.

### **Actions**

- Add a Metric: 

  - Specify Metric Name: Define the metric name. The selected name will be used in all tables and graphs to identify 
    this metric.
  
  - Point Metric Key: Enter the metric key. To use metric in your training code, call the ```arcee.send()``` method like: 
    ```arcee.send({ "metric_key": value })```.
  
  - Define Tendency: Pick a tendency value. Tendency helps determine the boundaries of metric values in relation to the 
    target value.
  
  - Specify Target Value: Enter the value you want to achieve for the metric.
  
  - Select Aggregate Function: Choose an aggregation function from the list provided. The aggregation function will be 
    applied if the metric has multiple recorded values within one second.
  
### **Tips**

- Achieving Goals: A green circle next to the metric name indicates that it has reached the target value according to the tendency.