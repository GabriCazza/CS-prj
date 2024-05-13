import streamlit as st
from datetime import datetime
import pytz
import time

def clock_main():
    timezone = pytz.timezone("Europe/Zurich")

    if 'auto_refresh' not in st.session_state:
        # Initialize auto refresh state
        st.session_state.auto_refresh = 0

    current_time = datetime.now(timezone).strftime("%H:%M:%S")
    
    st.title('Orologio in Tempo Reale')
    st.subheader(f"Ora corrente: {current_time}")

    # Trigger an auto-refresh every second
    if st.button("Refresh", key="1"):
        # This block won't actually execute because the script reruns first
        pass

    if st.session_state.auto_refresh == 0:
        # First load, no delay
        st.session_state.auto_refresh = 1
    else:
        # Wait a second then trigger the button click
        time.sleep(1)
        st.experimental_rerun()

def main():
    clock_main()

if __name__ == "__main__":
    main()
