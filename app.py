import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8080/sleep-api"

st.title("Smart Sleep Tracker")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Dashboard", "Data Sources", "API Info", "Prediction", "Team", "Register"])

# User Authentication (Simplified in Streamlit)
logged_in_user = st.session_state.get('logged_in_user')

def login():
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        try:
            response = requests.post(f"{API_BASE_URL}/user/login", json={"username": username, "password": password})
            response.raise_for_status()
            st.session_state['logged_in_user'] = username
            st.success(f"Logged in as {username}")
            st.rerun() # Refresh to update UI
        except requests.exceptions.RequestException as e:
            st.error(f"Login failed: {e}")


def logout():
    if st.sidebar.button("Logout"):
        del st.session_state['logged_in_user']
        st.info("Logged out")
        st.rerun()

if not logged_in_user and page != "Register":
    login()
elif logged_in_user:
    st.sidebar.write(f"Logged in as: {logged_in_user}")
    logout()

# --- Page Content ---
if page == "Overview":
    st.header("Project Overview")
    st.image("images/slee_banner1.jpg", caption="Sleep Analysis Banner", use_container_width=True)
    st.write("""
        Sleep quality is influenced by multiple factors. Our Smart Sleep Tracker combines real-time data and historical lifestyle patterns to uncover what really affects your sleep by estimating your next sleep cycle based on your current heartrate, room temperature and humidity.
    """)
    st.subheader("Key Features")
    st.markdown("""
        - 🌡️ **Environment Monitoring:** Track temperature and humidity.
        - ❤️ **Heart Rate Detection:** Monitor heartbeat and identify sleep disturbances.
        - 📚 **Data Integration:** Merge local sensor readings with Kaggle datasets.
        - 🔮 **AI-Based Prediction:** Estimate upcoming sleep quality.
    """)

elif page == "Dashboard":
    st.header("Sleep Dashboard")
    if logged_in_user:
        user_id = 1  # Replace with actual user ID retrieval
        try:
            sessions_response = requests.get(f"{API_BASE_URL}/sessions/{user_id}")
            sessions_response.raise_for_status()
            sessions_data = sessions_response.json()

            session_options = {
                session['sleep_id']: f"Session {session['sleep_id']} ({datetime.fromisoformat(session['start_time']).strftime('%Y-%m-%d %H:%M')})"
                for session in sessions_data
            }
            selected_session_id = st.selectbox("Select Sleep Session", options=session_options.keys(), format_func=lambda x: session_options[x])

            if selected_session_id:
                efficiency_response = requests.get(f"{API_BASE_URL}/efficiency/{user_id}/{selected_session_id}")
                efficiency_response.raise_for_status()
                efficiency_data = efficiency_response.json()

                log_response = requests.get(f"{API_BASE_URL}/log/{user_id}/{selected_session_id}")
                log_response.raise_for_status()
                log_data = log_response.json()

                st.subheader(f"Dashboard for Session: {session_options[selected_session_id]}")

                if efficiency_data:
                    labels = ['Light Sleep', 'REM Sleep', 'Deep Sleep']
                    values = [efficiency_data['light'], efficiency_data['rem'], efficiency_data['deep']]
                    fig_pie = px.pie(names=labels, values=values, title=f"Sleep Stage Breakdown - Efficiency: {efficiency_data['efficiency']:.2%}", hole=0.3)
                    st.plotly_chart(fig_pie)
                else:
                    st.warning("No sleep efficiency data for this session.")

                if log_data:
                    df_log = pd.DataFrame(log_data)
                    df_log['ts'] = pd.to_datetime(df_log['ts'], format='%d-%m-%Y %H:%M:%S')
                    fig_temp = px.line(df_log, x='ts', y='temperature', title='Temperature Over Time')
                    fig_humidity = px.line(df_log, x='ts', y='humidity', title='Humidity Over Time')
                    fig_heartrate = px.line(df_log, x='ts', y='heartrate', title='Heart Rate Over Time')
                    st.plotly_chart(fig_temp)
                    st.plotly_chart(fig_humidity)
                    st.plotly_chart(fig_heartrate)
                else:
                    st.warning("No sleep log data available for this session.")

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {e}")
        except requests.exceptions.HTTPError as e:
            st.error(f"Error fetching data: {efficiency_response.json().get('detail', 'An error occurred')}")
    else:
        st.info("Please log in to view the dashboard.")

elif page == "Data Sources":
    st.header("Data Sources")
    st.subheader("Primary")
    st.markdown("""
        - KY-015: Temperature & Humidity Sensor
        - KY-039: Heartbeat Sensor
        - Google Forms
    """)
    st.subheader("Secondary")
    st.markdown("""
        - [Kaggle Sleep Efficiency Dataset](https://www.kaggle.com/datasets/equilibriumm/sleep-efficiency)
        - ![](/images/sleep_efficiency.jpg)
        - [Kaggle Sleep Environment Dataset](https://www.kaggle.com/datasets/karthikiye/wearable-tech-sleep-quality/data)
        - ![](/images/sleep_quality.jpg)
        - [Sleep Health and Lifestyle Dataset](https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset)
        - ![](/images/sleep_lifestyle.jpg)
    """)
    st.info("Ensure the images are in a static `images` folder at the root of your Streamlit app or accessible via a URL.")

elif page == "API Info":
    st.header("API Overview")
    st.image("images/api_example.jpg", caption="API Overview Diagram", use_container_width=True)
    st.markdown("""
        - `/efficiency/{user_id}`: Predicted sleep efficiency and breakdown for latest session
        - `/log/{user_id}`: All logged environmental + heartrate data
        - `/latest/{user_id}`: Latest reading from sensors
        - `/user/login`: Authenticates a user
        - `/user/register`: Registers a new user with age, gender, exercise, and smoke info
        - `/user/edit`: Updates user profile info
    """)

elif page == "Prediction":
    st.header("Sleep Prediction")
    if logged_in_user:
        user_id = 1 # Replace with actual user ID retrieval
        try:
            sessions_response = requests.get(f"{API_BASE_URL}/sessions/{user_id}")
            sessions_response.raise_for_status()
            sessions_data = sessions_response.json()

            session_options = {session['sleep_id']: f"Session {session['sleep_id']} ({datetime.fromisoformat(session['start_time']).strftime('%Y-%m-%d')})" for session in sessions_data}
            selected_session_id = st.selectbox("Select Session", options=session_options.keys(), format_func=lambda x: session_options[x])

            if selected_session_id:
                efficiency_response = requests.get(f"{API_BASE_URL}/efficiency/{user_id}/{selected_session_id}")
                efficiency_response.raise_for_status()
                session_efficiency = efficiency_response.json()

                log_response = requests.get(f"{API_BASE_URL}/log/{user_id}/{selected_session_id}")
                log_response.raise_for_status()
                session_log = log_response.json()

                st.subheader(f"Session Details: {session_options[selected_session_id]}")
                st.write(f"Start Time: {session_efficiency['start_time']}")
                st.write(f"End Time: {session_efficiency['end_time']}")
                st.write(f"Sleep Efficiency: {session_efficiency['efficiency']:.2%}")
                st.write(f"Light Sleep: {session_efficiency['light']:.2%}")
                st.write(f"REM Sleep: {session_efficiency['rem']:.2%}")
                st.write(f"Deep Sleep: {session_efficiency['deep']:.2%}")
                st.write(f"Smoker: {'Yes' if session_efficiency['smoke'] else 'No'}")
                st.write(f"Exercise (sessions/week): {session_efficiency['exercise']}")

                if session_log:
                    df_session_log = pd.DataFrame(session_log)
                    df_session_log['ts'] = pd.to_datetime(df_session_log['ts'], format='%d-%m-%Y %H:%M:%S')
                    st.subheader("Environmental Data")
                    st.dataframe(df_session_log)

                    fig_temp = px.line(df_session_log, x='ts', y='temperature', title='Temperature Over Time')
                    fig_humidity = px.line(df_session_log, x='ts', y='humidity', title='Humidity Over Time')
                    fig_heartrate = px.line(df_session_log, x='ts', y='heartrate', title='Heart Rate Over Time')
                    st.plotly_chart(fig_temp)
                    st.plotly_chart(fig_humidity)
                    st.plotly_chart(fig_heartrate)
                else:
                    st.warning("No environmental data for this session.")

                # Efficiency History
                all_efficiency_response = requests.get(f"{API_BASE_URL}/efficiency/{user_id}")
                all_efficiency_response.raise_for_status()
                all_efficiency_data = all_efficiency_response.json()

                if all_efficiency_data:
                    df_history = pd.DataFrame(all_efficiency_data)
                    if 'start_time' in df_history.columns:
                        # Specify the DMY and time format for 'start_time' as well, if applicable
                        df_history['start_time'] = pd.to_datetime(df_history['start_time'], format='%Y-%m-%d %H:%M:%S') # Adjust format if needed
                        fig_history = px.line(df_history, x='start_time', y='efficiency', title='Sleep Efficiency Over Time')
                        st.plotly_chart(fig_history)
                    else:
                        st.warning("No 'start_time' column found in efficiency history data.")
                else:
                    st.warning("No sleep efficiency history available.")

        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching data: {e}")
        except requests.exceptions.HTTPError as e:
            st.error(f"Error fetching data: {sessions_response.json().get('detail', 'An error occurred')}")
    else:
        st.info("Please log in to view sleep prediction data.")

elif page == "Team":
    st.header("Team & Deliverables")
    st.subheader("Team")
    st.markdown("""
        - **Riccardo Mario Bonato:** Front End
        - **Rattanan Rung-Uthai:** Back End & API Design
    """)
    st.subheader("Deliverables")
    st.markdown("""
        This project was developed by a Year-2 student team from course 01219335 (Data Acquisition and Integration). Final deliverables include real-time data integration, predictive analytics, and a full-featured web dashboard.
    """)

elif page == "Register":
    st.header("User Registration")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    age = st.number_input("How old are you", min_value=1, step=1)
    gender = st.selectbox("What gender are you?", ["male", "female"])
    smoke = st.selectbox("Do you smoke?", ["No", "Yes"])
    exercise = st.number_input("Exercise sessions per week", min_value=0, max_value=7, step=1)

    if st.button("Register"):
        try:
            register_data = {
                "username": username,
                "password": password,
                "age": age,
                "gender": gender,
                "smoke": smoke == "Yes",
                "exercise": exercise
            }
            response = requests.post(f"{API_BASE_URL}/user/register", json=register_data)
            response.raise_for_status()
            st.success("Registration successful! Please log in.")
        except requests.exceptions.RequestException as e:
            st.error(f"Registration failed: {e}")
        except requests.exceptions.HTTPError as e:
            st.error(f"Registration failed: {response.json().get('detail', 'An error occurred')}")

# --- Footer ---
st.markdown("---")
st.markdown("&copy; 2025 Smart Sleep Tracker Project")