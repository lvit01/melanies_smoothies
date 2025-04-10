# Import Python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    Choose the fruits you want in your custom Smoothie!
    """
)

# User input for name on order
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your smoothie will be: ", name_on_order)

try:
    # Establish connection to Snowflake (assuming st.connection is correctly defined)
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Retrieve fruit options from Snowflake
    my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col('SEARCH_ON'))
    #st.dataframe(data=my_dataframe, use_container_width=True)
    #st.stop

    # Convert the Snowpark DataFrame to a Pandas DataFrame so we can use the LOC function
    pd_df = my_dataframe.to_pandas()
    #st.dataframe(pd_df)
    #st.stop()

    # Multi-select for choosing ingredients
    ingredients_list = st.multiselect(
        'Choose up to 5 ingredients:'
        , my_dataframe
        , max_selections=5
        )

    # Process ingredients selection
    if ingredients_list:
        ingredients_string = ''

        for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ' '

            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            # st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

            st.subheader(fruit_chosen + ' Nutrition Information')
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

        # st.write(ingredients_string)

        # SQL statement to insert order into database (assuming proper handling of SQL injection risk)
        my_insert_stmt = """INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                            VALUES ('{}', '{}')""".format(ingredients_string, name_on_order)

        # Button to submit order
        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            try:
                # Execute SQL insert statement
                session.sql(my_insert_stmt).collect()
                st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
            except Exception as e:
                st.error(f"Failed to submit order: {str(e)}")

except Exception as ex:
    st.error(f"An error occurred: {str(ex)}")
