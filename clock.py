import streamlit as st
from datetime import datetime

def clock_main():
    st.title('Orologio in Tempo Reale')

    # Definisce un posto fisso per l'orologio nella pagina
    placeholder = st.empty()

    # Aggiorna l'orologio ogni secondo
    while True:
        # Ottiene l'ora corrente
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Aggiorna l'orologio nello stesso posto
        placeholder.subheader(f'Ora corrente: {current_time}')
        
        # Pausa di un secondo prima del prossimo aggiornamento
        datetime.sleep(1)

if __name__ == "__main__":
    clock_main()
