import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import base64

st.title("Product Relationship Algorithm")
st.markdown("Import a csv file in the correct format and it will generate an output of products with positive relationships. The results can then be used to build bundles for upsell opportunities. Also, the results can be used for basic recommendations - if you buy a specific item you are likely to be interested in an item with a positive relationship.")
st.markdown("The headings for importing to the model: __InvoiceNo__ for order id; __StockCode__ for product id/sku; __Description__ as the product name or description.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    data.to_csv('data/upload.csv')    
    if st.checkbox('Show Imported Data'):
        st.subheader("Imported Dataset")
        st.write(data)
    else:
        ''
############################################################################
### THE MODEL STARTS HERE ###
###########################################################################
try:
    #import data
    data_import = pd.read_csv('data/upload.csv')
    select = data_import[['InvoiceNo','StockCode']]

    import time
    '__Starting a long computation...__'
    # Add a placeholder
    latest_iteration = st.empty()
    bar = st.progress(0)

    #import packages
    import pandas as pd
    import numpy as np
    from itertools import combinations, groupby
    from collections import Counter
    #all possible pairs

    orders = select.values

    # Generator that yields item pairs, one at a time
    def get_item_pairs(order_item):
        
        # For each order, generate a list of items in that order
        for order_id, order_object in groupby(orders, lambda x: x[0]):
            item_list = [item[1] for item in order_object]      
        
            # For each item list, generate item pairs, one at a time
            for item_pair in combinations(item_list, 2):
                yield item_pair                                      


    # Counter iterates through the item pairs returned by our generator and keeps a tally of their occurrence
    Counter(get_item_pairs(orders))

    import sys
    from IPython.display import display

    orders = select.set_index('InvoiceNo')['StockCode'].rename('item_id')
    display(orders.head(10))
    type(orders)


    #Helper function to the main association rules function
    # Returns frequency counts for items and item pairs
    def freq(iterable):
        if type(iterable) == pd.core.series.Series:
            return iterable.value_counts().rename("freq")
        else: 
            return pd.Series(Counter(iterable)).rename("freq")

        
    # Returns number of unique orders
    def order_count(order_item):
        return len(set(order_item.index))


    # Returns generator that yields item pairs, one at a time
    def get_item_pairs(order_item):
        order_item = order_item.reset_index().as_matrix()
        for order_id, order_object in groupby(order_item, lambda x: x[0]):
            item_list = [item[1] for item in order_object]
                
            for item_pair in combinations(item_list, 2):
                yield item_pair
                

    # Returns frequency and support associated with item
    def merge_item_stats(item_pairs, item_stats):
        return (item_pairs
                    .merge(item_stats.rename(columns={'freq': 'freqA', 'support': 'supportA'}), left_on='item_A', right_index=True)
                    .merge(item_stats.rename(columns={'freq': 'freqB', 'support': 'supportB'}), left_on='item_B', right_index=True))


    # Returns name associated with item
    def merge_item_name(rules, item_name):
        columns = ['itemA','itemB','freqAB','supportAB','freqA','supportA','freqB','supportB', 
                'confidenceAtoB','confidenceBtoA','lift']
        rules = (rules
                    .merge(item_name.rename(columns={'item_name': 'itemA'}), left_on='item_A', right_on='item_id')
                    .merge(item_name.rename(columns={'item_name': 'itemB'}), left_on='item_B', right_on='item_id'))
        return rules[columns] 

    #association rule function
    def association_rules(order_item, min_support):

        print("Starting order_item: {:22d}".format(len(order_item)))


        # Calculate item frequency and support
        item_stats             = freq(order_item).to_frame("freq")
        item_stats['support']  = item_stats['freq'] / order_count(order_item) * 100


        # Filter from order_item items below min support 
        qualifying_items       = item_stats[item_stats['support'] >= min_support].index
        order_item             = order_item[order_item.isin(qualifying_items)]

        print("Items with support >= {}: {:15d}".format(min_support, len(qualifying_items)))
        print("Remaining order_item: {:21d}".format(len(order_item)))


        # Filter from order_item orders with less than 2 items
        order_size             = freq(order_item.index)
        qualifying_orders      = order_size[order_size >= 2].index
        order_item             = order_item[order_item.index.isin(qualifying_orders)]

        print("Remaining orders with 2+ items: {:11d}".format(len(qualifying_orders)))
        print("Remaining order_item: {:21d}".format(len(order_item)))


        # Recalculate item frequency and support
        item_stats             = freq(order_item).to_frame("freq")
        item_stats['support']  = item_stats['freq'] / order_count(order_item) * 100


        # Get item pairs generator
        item_pair_gen          = get_item_pairs(order_item)


        # Calculate item pair frequency and support
        item_pairs              = freq(item_pair_gen).to_frame("freqAB")
        item_pairs['supportAB'] = item_pairs['freqAB'] / len(qualifying_orders) * 100

        print("Item pairs: {:31d}".format(len(item_pairs)))


        # Filter from item_pairs those below min support
        item_pairs              = item_pairs[item_pairs['supportAB'] >= min_support]

        print("Item pairs with support >= {}: {:10d}\n".format(min_support, len(item_pairs)))


        # Create table of association rules and compute relevant metrics
        item_pairs = item_pairs.reset_index().rename(columns={'level_0': 'item_A', 'level_1': 'item_B'})
        item_pairs = merge_item_stats(item_pairs, item_stats)
        
        item_pairs['confidenceAtoB'] = item_pairs['supportAB'] / item_pairs['supportA']
        item_pairs['confidenceBtoA'] = item_pairs['supportAB'] / item_pairs['supportB']
        item_pairs['lift']           = item_pairs['supportAB'] / (item_pairs['supportA'] * item_pairs['supportB'])
        
        
        # Return association rules sorted by lift in descending order
        return item_pairs.sort_values('lift', ascending=False)

    rules = association_rules(orders, 0.01)

    rules['Product_Relationship'] = np.nan

    def ProdRel(x):
        if x['lift'] ==1:
            return "No Relationship"
        elif x['lift'] <1:
            return "Negative Relationship"
        else:
            return "Positive Relationship"

    rules['Product_Relationship'] = rules.apply(lambda x: ProdRel(x), axis=1)
    final_rules = rules[rules['Product_Relationship']=='Positive Relationship']
    join = data_import[['StockCode','Description']]
    join = join.drop_duplicates()
    final_rules = pd.merge(final_rules, join, how='left', left_on='item_A', right_on='StockCode')
    final_rules = final_rules.rename(columns={'Description':'DescriptionA'})
    final_rules = final_rules.drop_duplicates()
    final_rules = pd.merge(final_rules, join, how='left', left_on='item_B', right_on='StockCode')
    final_rules = final_rules.rename(columns={'Description':'DescriptionB'})
    final_rules = final_rules.drop_duplicates()
    final_rules['flag'] = np.where(final_rules['DescriptionA']==final_rules['DescriptionB'], 1, 0)
    final_rules = final_rules[final_rules['flag']==0]
    final_rules = final_rules[['DescriptionA', 'DescriptionB', 'freqAB', 'freqAB', 'confidenceAtoB', 'confidenceBtoA', 'lift', 'Product_Relationship']]

    final_rules.to_csv('relationship.csv')

    for i in range(100):
    # Update the progress bar with each iteration.
        latest_iteration.text(f'Iteration {i+1}')
        bar.progress(i + 1)
        time.sleep(0.1)

    '__...and now we\'re done!__'
############################################################################
### THE MODEL ENDS HERE ###
###########################################################################
except:
    ''

@st.cache(persist=True)
def load_data():
    data = pd.read_csv('relationship.csv')
    return data

#load data 
try:
    data = load_data()

    st.subheader("Relationship Table")

    #filter
    products = st.sidebar.multiselect(
        'Select Product A',
        (data.DescriptionA.unique())
    )

    #display
    if products == []:
        data = data
    else:
        data = data[data['DescriptionA'].isin(products)]
    st.dataframe(data.head())

    count = data['DescriptionA'].nunique()
    freq_Ave = data['freqAB'].mean()
    st.write('Number of Products with Positive Relationships __%i__' % count)
    st.write('Average times in basket together __%i__' % freq_Ave)

    csv = data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (click and save as &lt;some_name&gt;.csv)'
    st.markdown(href, unsafe_allow_html=True)

    import os
    #delete files button
    if st.button('Delete Uploaded and Output Files'):
       os.remove('data/upload.csv')
       os.remove('relationship.csv')
    else:
        ''    

except:
    st.write('__NO DATA PLEASE UPLOAD TO RUN THE APRIORI ALGO__. Make sure that the data is in the above mentioned format.')