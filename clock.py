import streamlit as st
from datetime import datetime

def clock_main():
    if 'last_update' not in st.session_state or (datetime.now() - st.session_state.last_update).seconds >= 1:
        st.session_state.current_time = datetime.now().strftime("%H:%M:%S")
        st.session_state.last_update = datetime.now()

    st.title('Orologio in Tempo Reale')
    placeholder = st.empty()
    placeholder.subheader(f"Ora corrente: {st.session_state.current_time}")
