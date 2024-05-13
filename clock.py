import streamlit as st
from datetime import datetime
import pytz

def display_time():
    # Set timezone to Zurich
    timezone = pytz.timezone("Europe/Zurich")
    # Display current Zurich time formatted as H:M:S
    current_time = datetime.now(timezone).strftime("%H:%M:%S")
    return current_time

def clock_main():
    st.title('Orologio in Tempo Reale')
    
    # Placeholder for the time display
    time_placeholder = st.empty()
    
    # Initialize or update the session state variable
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True

    # Display the time
    current_time = display_time()
    time_placeholder.subheader(f"Ora corrente: {current_time}")
    
    # Use a button to trigger re-runs which will refresh the time display
    if st.button("Refresh Time"):
        st.session_state.auto_refresh = not st.session_state.auto_refresh

    # To ensure that the app updates automatically every second
    st.experimental_rerun()

if __name__ == "__main__":
    clock_main()

