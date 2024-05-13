import streamlit as st
from datetime import datetime
import pytz

def clock_main():
    # Set the timezone to Zurich
    timezone = pytz.timezone("Europe/Zurich")
    
    # Check the last update or initialize it
    if 'last_update' not in st.session_state or (datetime.now(timezone) - st.session_state.last_update).total_seconds() >= 1:
        # Update the current time in the correct timezone
        st.session_state.current_time = datetime.now(timezone).strftime("%H:%M:%S")
        st.session_state.last_update = datetime.now(timezone)
    
    st.title('Orologio in Tempo Reale')
    placeholder = st.empty()
    placeholder.subheader(f"Ora corrente: {st.session_state.current_time}")
    
    # Trigger a rerun of the app approximately every second
    st.experimental_rerun()
