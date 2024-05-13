import streamlit as st

def main():
    st.title('Orologio in Tempo Reale')
    
    # Embed a publicly available JavaScript clock
    # This example uses a generic clock URL which you should replace with the actual URL of the clock you want to embed
    clock_html = """
    <iframe src='https://free.timeanddate.com/clock/i8ifsfw7/n268/szw160/szh160/hbw0/hbh0/hbc000/cf100/hgr0/fav0/fiv0/mqcfff/mqs2/mql3/mqw1/mqd78/mhcfff/mhs2/mhl3/mhw1/mhd78/mmv0/hwm2/hhcbbb/hhs2/hmcbbb/hms2/hscbbb' frameborder='0' width='160' height='160'></iframe>
    """
    
    # Display the HTML iframe in Streamlit
    st.markdown(clock_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

