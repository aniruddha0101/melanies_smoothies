import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the Fruits you want in your custom smoothie!")

# Input for name on the order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The Name of smoothies will be:', name_on_order)

# Get the session and fetch fruit options
session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
fruit_names = [row.FRUIT_NAME for row in my_dataframe]

# Display multiselect for ingredients
ingredients_list = st.multiselect("Select Fruits", options=fruit_names)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        try:
            # Replace with your alternative API URL
            response = requests.get(f"https://api.example.com/nutrition?fruit={fruit_chosen}", timeout=10)
            response.raise_for_status()  # Check for HTTP errors
            data = response.json()
            st.dataframe(data, use_container_width=True)
        except requests.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

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
        session.sql(my_insert_stmt).collect()
        
        # Personalized success message
        st.success(f'Your Smoothie for "{name_on_order}" is ordered! ✅')
    else:
        st.warning('Please enter a name and select at least one ingredient.')
