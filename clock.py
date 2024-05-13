import streamlit as st

def main():
    st.title('Stylish Clock')
    # Replace 'your_clock_url.html' with the URL where your clock is hosted
    clock_html = """
    <iframe src='clock.html' width='210' height='210' frameborder='0'></iframe>
    """
    st.markdown(clock_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
