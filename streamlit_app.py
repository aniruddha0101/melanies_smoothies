import streamlit as st
import requests  # Ensure this import is included
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Input for name on the order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name of the smoothie will be:', name_on_order)

# Get the session and fetch fruit options
session = get_active_session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Display multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Use the list of fruit names
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        if fruit_chosen in pd_df['FRUIT_NAME'].values:
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.write(f'The search value for {fruit_chosen} is {search_on}.')

            st.subheader(f'{fruit_chosen} Nutrition Information')
            try:
                fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
                fruityvice_response.raise_for_status()  # Raise an exception for HTTP errors
                fruit_data = fruityvice_response.json()
                st.write(f"Nutrition data for {fruit_chosen}: {fruit_data}")
            except requests.ConnectionError:
                st.error(f"Failed to connect to Fruityvice API. Please check your internet connection.")
            except requests.HTTPError as e:
                st.error(f"HTTP error occurred: {e}")
            except requests.RequestException as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning(f"Fruit {fruit_chosen} not found in the options.")

# Submit order button
if st.button('Submit Order'):
    if ingredients_list and name_on_order:
        ingredients_string = ', '.join(ingredients_list)
        
        # Escape single quotes in the inputs to avoid SQL injection
        name_on_order_escaped = name_on_order.replace("'", "''")
        ingredients_string_escaped = ingredients_string.replace("'", "''")
        
        # Construct the SQL query
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order) 
            VALUES ('{ingredients_string_escaped}', '{name_on_order_escaped}')
        """
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your smoothie order for "{name_on_order}" has been placed! ✅')
        except Exception as e:
            st.error(f"An error occurred while placing the order: {e}")
    else:
        st.warning('Please enter a name and select at least one ingredient.')



import requests
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
st.text(fruityvice_response)
