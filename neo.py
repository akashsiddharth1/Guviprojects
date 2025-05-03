# Import necessary libraries

import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
import pandas as pd
from datetime import datetime

#Creating Mysql Database connection

db_connection = mysql.connector.connect(
    host='localhost',
    user='root',  
    password='998800', 
    database='nasa_db'  
)
cursor = db_connection.cursor()

# Seting up Page configuration

st.set_page_config(
    page_title="NASA Asteroids Tracker",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and welcome text for the dashboard

st.markdown("<h1 style='text-align: center; color: black;'>☄️ NASA Asteroids Tracker </h1>", unsafe_allow_html=True)
st.markdown("""
Welcome to the NASA Asteroids Tracker — an interactive dashboard to monitor near-Earth objects (NEOs) using live and historical data from NASA’s API.
This project visualizes and analyzes asteroid data such as their size, speed, close approach dates, and potential hazards. Use the filters and tools to explore the cosmos and see how close asteroids come to Earth.
""")
st.divider()

# Sidebar config
st.sidebar.title(" Asteroids Tracker Menu") # Title of sidebar

# Navigation menu using option_menu

with st.sidebar:
    st.sidebar.markdown("#### 🌍 Navigation ###") # subtitle
    selected = option_menu(
    menu_title="",
    options=["Filter", "Queries"],
    icons=["filter", "question"],
    menu_icon="",
    default_index=0
    )

# Execute filter

if selected == "Filter":
    st.title("🧮 Filter Asteroids")
    c1,ca,c2,cb,c3 = st.columns([0.2,0.1,0.2,0.1,0.2]) # slidebar columns with 20%,10%,20%,10%,20% space values

# Column 1: Filters for size and distance
    with c1:
        # Lunar distance
        lunar = st.slider("Lunar distance", value = (0,200))

        # Diameter
        min_diam = st.slider("Min Estimated Diameter (km)", value = (0.00, 1.00))
        max_diam = st.slider("Max Estimated Diameter (km)", value = (0.00, 1.40))

# Column 2: Filters for velocity, AU, and hazard
    with c2:
        # Velocity
        velocity = st.slider("Relative velocity km/h",value = (11900.00, 136268.00))
        # astronomical
        astro = st.slider("Astronomical unit", value=(0.00, 0.5))

        # Hazardous Checkbox
        hazardous = st.selectbox("Potentially Hazardous",  options= [0,1],index=0)
    
 # Column 3: Filters for date range   
    with c3:
        # date range
        start_date = st.date_input("Start Date", datetime(2024, 1, 1))
        end_date = st.date_input("End Date", datetime(2025, 4, 13))


 # Button to execute filter query
    button = st.button("Filter")

    # SQL query to filter data

    query = """
              SELECT
                  asteroids.id, asteroids.name, asteroids.estimated_diameter_min_km,
                  asteroids.estimated_diameter_max_km, asteroids.is_potentially_hazardous_asteroid,
                  close_approach.close_approach_date, close_approach.relative_velocity_kmph, close_approach.astronomical, 
                  close_approach.miss_distance_lunar
              FROM asteroids
              JOIN close_approach ON asteroids.id = close_approach.neo_reference_id
              WHERE asteroids.estimated_diameter_min_km BETWEEN %s AND %s
                AND asteroids.estimated_diameter_max_km BETWEEN %s AND %s
                AND close_approach.relative_velocity_kmph BETWEEN %s AND %s
                AND close_approach.astronomical BETWEEN %s AND %s
                AND close_approach.miss_distance_lunar BETWEEN %s AND %s
                AND close_approach.close_approach_date BETWEEN %s AND %s
                AND asteroids.is_potentially_hazardous_asteroid = %s
                """
 
 # Parameters passed into query

    params = [
            min_diam[0],min_diam[1],
            max_diam[0],max_diam[1],
            velocity[0],velocity[1],
            astro[0], astro[1],
            lunar [0], lunar[1],
            start_date, end_date,
            hazardous
            ]

      # --- Execute the query ---
    if button:
        cursor.execute(query, params)
        result = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]  #  Get column names 
         
        df = pd.DataFrame(result, columns=columns) # Convert to DataFrame 

        # df.drop_duplicates(inplace=True)

        st.subheader("Filtered Asteroids")         # Show the result 
        st.dataframe(df)

 # Queries section       

elif selected == "Queries":
    option = st.selectbox("Select your query", [
        '1.Count how many times each asteroid has approached Earth',
        '2. Average velocity of each asteroid over multiple approaches',
        '3.List top 10 fastest asteroids',
        '4.Find potentially hazardous asteroids that have approached Earth more than 3 times',
        '5.Find the month with the most asteroid approaches',
        '6.Get the asteroid with the fastest ever approach speed',
        '7.Sort asteroids by maximum estimated diameter (descending)',
        '8.Asteroids whose closest approach is getting nearer over time',
        '9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth.',
        '10.List names of asteroids that approached Earth with velocity > 50,000 km/h',
        '11.Count how many approaches happened per month',
        '12.Find asteroid with the highest brightness (lowest magnitude value)',
        '13.Get number of hazardous vs non-hazardous asteroids',
        '14.Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance.',
        '15.Find asteroids that came within 0.05 AU(astronomical distance)',
        '16.Average Miss Distance for Each Asteroid (Approaching Earth)',
        '17.Fastest Hazardous Asteroid Per Year',
        '18.Asteroids with Large Diameters That Approached Closest',
        '19.Total Number of Approaches per Asteroid Along with Brightness',
        '20.Top 10 Asteroids That Came Closest to Earth by Lunar Distance',
        '21.Yearly Count of Potentially Hazardous Asteroid Approaches',
        '22.Longest Time Span Between First and Last Approach of Each Asteroid'
    ])

# Each if-block runs a different query based on user selection

    if option == '1.Count how many times each asteroid has approached Earth':
        cursor.execute("""
            SELECT neo_reference_id AS asteroid_id, COUNT(*) AS approach_count
            FROM close_approach
            WHERE orbiting_body = 'Earth'
            GROUP BY neo_reference_id
        """)
    
    elif option == '2. Average velocity of each asteroid over multiple approaches':
        cursor.execute("""
            SELECT neo_reference_id AS asteroid_id, AVG(relative_velocity_kmph) AS avg_velocity_kmph
            FROM close_approach
            GROUP BY neo_reference_id
        """)

    elif option == '3.List top 10 fastest asteroids':
        cursor.execute("""
            SELECT name, relative_velocity_kmph FROM close_approach
            JOIN asteroids
            ON asteroids.id = close_approach.neo_reference_id
            ORDER BY relative_velocity_kmph DESC
            LIMIT 10
        """)

    elif option == '4.Find potentially hazardous asteroids that have approached Earth more than 3 times':
        cursor.execute("""
            SELECT a.id AS asteroid_id, a.name, COUNT(*) AS approach_count
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE a.is_potentially_hazardous_asteroid = TRUE AND c.orbiting_body = 'Earth'
            GROUP BY a.id, a.name
            HAVING approach_count > 3;
        """)

    elif option == '5.Find the month with the most asteroid approaches':
        cursor.execute("""
            SELECT MONTH(close_approach_date) AS approach_month, COUNT(*) AS approach_count
            FROM close_approach
            GROUP BY approach_month
            ORDER BY approach_count DESC
            LIMIT 1
        """)

    elif option == '6.Get the asteroid with the fastest ever approach speed':
        cursor.execute("""
            SELECT neo_reference_id AS asteroid_id, 
            MAX(relative_velocity_kmph) AS fastest_velocity_kmph
            FROM close_approach
            GROUP BY asteroid_id
            ORDER BY fastest_velocity_kmph DESC
            LIMIT 1
        """)

    elif option == '7.Sort asteroids by maximum estimated diameter (descending)':
        cursor.execute("""
            SELECT id AS asteroid_id, name, estimated_diameter_max_km
            FROM asteroids
            ORDER BY estimated_diameter_max_km DESC;
        """)

    elif option == '8.Asteroids whose closest approach is getting nearer over time':
        cursor.execute("""
            SELECT neo_reference_id AS asteroid_id, close_approach_date, miss_distance_km
            FROM close_approach
            WHERE orbiting_body = 'Earth'
            ORDER BY neo_reference_id, close_approach_date;
        """)

    elif option == '9.Display the name of each asteroid along with the date and miss distance of its closest approach to Earth.':
        cursor.execute("""
            SELECT a.name, c.close_approach_date, c.miss_distance_km
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE (a.id, c.miss_distance_km) IN (
                SELECT neo_reference_id, MIN(miss_distance_km)
                FROM close_approach
                GROUP BY neo_reference_id
            );
        """)

    elif option == '10.List names of asteroids that approached Earth with velocity > 50,000 km/h':
        cursor.execute("""
            SELECT DISTINCT a.name
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.relative_velocity_kmph > 50000
        """)

    elif option == '11.Count how many approaches happened per month':
        cursor.execute("""
            SELECT MONTH(close_approach_date) AS approach_month, COUNT(*) AS monthly_approach_count
            FROM close_approach
            GROUP BY approach_month;
        """)

    elif option == '12.Find asteroid with the highest brightness (lowest magnitude value)':
        cursor.execute("""
            SELECT id AS asteroid_id, name, absolute_magnitude_h AS brightness_magnitude
            FROM asteroids
            ORDER BY absolute_magnitude_h ASC
            LIMIT 1;
        """)

    elif option == '13.Get number of hazardous vs non-hazardous asteroids':
        cursor.execute("""
            SELECT is_potentially_hazardous_asteroid, COUNT(*) AS asteroid_count
            FROM asteroids
            GROUP BY is_potentially_hazardous_asteroid;
        """)

    elif option == '14.Find asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance.':
        cursor.execute("""
            SELECT a.name, c.close_approach_date, c.miss_distance_lunar
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.miss_distance_lunar < 1;
        """)

    elif option == '15.Find asteroids that came within 0.05 AU(astronomical distance)':
        cursor.execute("""
            SELECT a.name, c.close_approach_date, c.astronomical AS distance_au
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.astronomical < 0.05;
        """)

    elif option == '16.Average Miss Distance for Each Asteroid (Approaching Earth)': 
        cursor.execute("""
            SELECT 
            a.name AS asteroid_name, AVG(c.miss_distance_km) AS avg_miss_distance_km
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.orbiting_body = 'Earth'
            GROUP BY a.name;
        """)

    elif option == '17.Fastest Hazardous Asteroid Per Year': 
        cursor.execute("""
            SELECT 
            YEAR(c.close_approach_date) AS approach_year,
            a.name AS hazardous_asteroid,
            MAX(c.relative_velocity_kmph) AS max_velocity
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE a.is_potentially_hazardous_asteroid = TRUE
            GROUP BY approach_year, a.name
            ORDER BY max_velocity DESC;
        """)

    elif option == '18.Asteroids with Large Diameters That Approached Closest': 
        cursor.execute("""
            SELECT 
            a.name,
            a.estimated_diameter_max_km,
            c.miss_distance_km,
            c.close_approach_date
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE a.estimated_diameter_max_km > 1
            ORDER BY c.miss_distance_km ASC
            LIMIT 10;
        """)

    elif option == '19.Total Number of Approaches per Asteroid Along with Brightness': 
        cursor.execute("""
            SELECT 
            a.name,
            COUNT(*) AS total_approaches,
            a.absolute_magnitude_h AS brightness_magnitude
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            GROUP BY a.name, a.absolute_magnitude_h
            ORDER BY total_approaches DESC;
        """)

    elif option == '20.Top 10 Asteroids That Came Closest to Earth by Lunar Distance': 
        cursor.execute("""
            SELECT 
            a.name,
            c.close_approach_date,
            c.miss_distance_lunar
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.orbiting_body = 'Earth'
            ORDER BY c.miss_distance_lunar ASC
            LIMIT 10;
        """)

    elif option == '21.Yearly Count of Potentially Hazardous Asteroid Approaches': 
        cursor.execute("""
            SELECT 
            YEAR(c.close_approach_date) AS year,
            COUNT(*) AS hazardous_approaches
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE a.is_potentially_hazardous_asteroid = TRUE
            GROUP BY year
            ORDER BY year;
        """)

    elif option == '22.Longest Time Span Between First and Last Approach of Each Asteroid': 
        cursor.execute("""
            SELECT 
            a.name AS asteroid_name,
            MIN(c.close_approach_date) AS first_approach,
            MAX(c.close_approach_date) AS last_approach,
            DATEDIFF(MAX(c.close_approach_date), MIN(c.close_approach_date)) AS days_tracked
            FROM asteroids a
            JOIN close_approach c ON a.id = c.neo_reference_id
            WHERE c.orbiting_body = 'Earth'
            GROUP BY a.name
            ORDER BY days_tracked DESC
            LIMIT 10;
        """)

 # Fetch and display the result after any query is selected and executed
    result = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]

    data = pd.DataFrame(result, columns = columns)
    st.dataframe(data)




# # Tables sidebar

# with st.sidebar:
#     st.sidebar.markdown ("### Tables ###")
#     selected = option_menu(
#     menu_title="",
#     options=["Asteroids", "close approach"],
#     icons=["table", "table"],
#     menu_icon="",
#     default_index=0
# )
    
# Execute
# if selected == "Asteroids":
#     cursor.execute("""
#         select * from nasa_db.asteroids
#         """)
#     rows = cursor.fetchall()

#     columns = [desc[0] for desc in cursor.description] # --- Get column names ---

#     df = pd.DataFrame(rows, columns=columns) # --- Convert to DataFrame ---

#     st.subheader("Asteroids table")  # --- Show the result ---
#     st.dataframe(df)

# elif selected == "close approach":
#     cursor.execute("""
#         select * from nasa_db.close_approach
#         """)
#     rows = cursor.fetchall()

#     columns = [desc[0] for desc in cursor.description] # --- Get column names ---

#     df = pd.DataFrame(rows, columns=columns) # --- Convert to DataFrame ---

#     st.subheader("Close approach table")  # --- Show the result ---
#     st.dataframe(df)

# db_connection.close() ***/

# # Settinngs 
# st.sidebar.markdown("### Settings ###")
# on = st.sidebar.toggle("Dark mode") # dark mode toggle switch






