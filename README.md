# Machine Learning Prediction of High School Graduation Rates  

*Cohort 28 (Fall 2022)  Capstone Project for the Certificate of Data Science at Georgetown University School of Continuing Studies*    

---

## Abstract  

Imagine being able to predict the factors leading to dropout and graduation rates in the United States. In 2018–19, the Adjusted Cohort Graduation Rate (ACGR) ranged from 69% in the District of Columbia to 92% in Iowa. Forty states reported ACGRs ranging from 80% to less than 90%. What accounts for this discrepancy? A staggering 2,829 unique schools had less than 25% graduation rate between 2010-2019. Using a regression model, our project examined over 80,000 instances and aimed to reveal the most significant contributing factors to graduation rates as well as producing a model to predict graduation rate based on features of individual schools. Our top performing model was a random forest model with accuracy 0.709 and root mean square error of 10.48 percentage points. We also produced a random forest classification model which segments public high schools into two groups, <90% and ≥90% graduation rate, with an F1 score of 0.789. These two models could be utilized by secondary education stakeholders for planning or targeted intervention.  

---

## File Organization  

**1_Ingestion_and_Wrangling** --> wrangle, clean, and merge raw data from worm store  

**2_Exploratory_Data_Analysis** --> summary statistics and graphical analysis  

**3_Feature_Engineering** --> add and remove features using imputation and feature importances  

**4_Modeling** --> train and test a variety of models  

**5_Visualization** --> static images and interactive visualization  

**6_Deployment** --> accept user input and generate predictions on the best model  

**7_Validation** --> validation of models  

**8_Paper_and_Slides** --> final project report and presentation

**data** --> processed dataframes stored as csvs for use by other notebooks, also metadata csv  

**data_docs** --> description of features and provenance of the datasets  

**logs** --> logs from modeling  

**model_files** --> saved model files for deployment  

**.gitignore** --> a list of file types to remain untracked by Git

**LICENSE** --> software license for this project  

**requirements.txt** --> run `pip install -r requirements.txt` to load dependencies for the project
