import streamlit as st
from datetime import datetime, timedelta
import pytz
import time

def main():
    # Set the timezone to Zurich
    timezone = pytz.timezone("Europe/Zurich")

    # Initialize the current_time in session state if it doesn't exist
    if 'current_time' not in st.session_state:
        st.session_state.current_time = datetime.now(timezone).strftime("%H:%M:%S")

    st.title('Orologio in Tempo Reale')

    # Display the clock
    time_display = st.empty()  # This creates a placeholder to update the time

    while True:
        # Update the time every second
        current_time = datetime.now(timezone).strftime("%H:%M:%S")
        time_display.subheader(f"Ora corrente: {current_time}")
        time.sleep(1)  # Delay for 1 second before updating the time again

if __name__ == "__main__":
    st.experimental_singleton()  # Ensures the app does not restart every time
    main()

