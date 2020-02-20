# Association-Rules
 Association rule mining, at a basic level, involves the use of machine learning models to analyze data for patterns, or co-occurrence, in a database. It identifies frequent if-then associations, which are called association rules.

## Built With

* [Python 3.7](https://www.python.org/downloads/release/python-370/) - More info

### Libraries to install 

```
pip install -r requirements.txt
```

or pip install 
```
pandas
numpy
streamlit
altair
pydec
```

### Data

* [Find the Data here]() - Download the public dataset from here

## The App
This is a very basic app aimed at simplifying the management of running computations for a semi custom dataset. The point was to enable an analyst/ Data Scientist to simply upload the dataset and have the computations run automatically. Then Save the the outputs in csv format. The task can also be completed by a merchandising team. 

The concept can be taken further by have a DB connecter in the app with some customer parameters that can be passed through by the app. Such as dates between or product category etc. Then also potentially a action button like "Run Model" to start the computations. 

For now you can clone or download the reposit and simply run the streamlit app. I have also included an example dataset for importing. Have fun. 

```
streamlit run app.py
```

## The Model

You can find the code in the model model.py file 

### Deployment options

* Docker Setup. 
* Include the computations as a part of your ETL process (I use [KNIME](https://www.knime.com/)) - Include it as a step before writing the final customer lifetime table to your Data Warehouse.

## Author

* **Francois van Heerden** - *Experience* - [LinkedIn Profile](https://www.linkedin.com/in/francois-van-heerden-9589825a/)

## Acknowledgments

* Found inspiration from multiple fellow Data Scientists in the open source community
* But I would like to specifically highlight this post [Association Rule Mining via Apriori Algorithm in Python](https://stackabuse.com/association-rule-mining-via-apriori-algorithm-in-python/) 
