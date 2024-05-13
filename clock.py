import streamlit as st
from datetime import datetime, timedelta
import pytz

def clock_main():
    timezone = pytz.timezone("Europe/Zurich")
    
    # Initialize session state variables if they do not exist
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now(timezone) - timedelta(seconds=1)  # Ensures immediate update
    
    # Check if more than one second has passed
    current_time = datetime.now(timezone)
    if (current_time - st.session_state.last_update).total_seconds() >= 1:
        # Update the stored time and last update timestamp
        st.session_state.current_time = current_time.strftime("%H:%M:%S")
        st.session_state.last_update = current_time

    # Display the title and the time
    st.title('Orologio in Tempo Reale')
    st.subheader(f"Ora corrente: {st.session_state.current_time}")
