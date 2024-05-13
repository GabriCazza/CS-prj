import streamlit as st

def clock_main():
    st.title('Stylish Clock')
    
    # Define the clock HTML with CSS and JavaScript
    clock_html = """
    <div style="font-family: Arial, sans-serif; display: flex; justify-content: center;">
        <div style="position: relative; width: 200px; height: 200px; border-radius: 50%; background: white; border: 8px solid #333; display: flex; align-items: center; justify-content: center;">
            <div style="position: absolute; width: 160px; height: 160px; border-radius: 50%; background: #EEE;"></div>
            <div id="hour" style="position: absolute; background: black; height: 50px; width: 6px; transform-origin: 50% 100%;"></div>
            <div id="minute" style="position: absolute; background: black; height: 70px; width: 4px; transform-origin: 50% 100%;"></div>
            <div id="second" style="position: absolute; background: red; height: 90px; width: 2px; transform-origin: 50% 100%;"></div>
        </div>
    </div>
    <script>
        function updateClock() {
            var now = new Date();
            var second = now.getSeconds() * 6;
            var minute = now.getMinutes() * 6 + second / 60;
            var hour = ((now.getHours() % 12) / 12) * 360 + 90 + minute / 12;
            
            document.getElementById('hour').style.transform = 'rotate(' + hour + 'deg)';
            document.getElementById('minute').style.transform = 'rotate(' + minute + 'deg)';
            document.getElementById('second').style.transform = 'rotate(' + second + 'deg)';
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
    """
    
    # Display the HTML clock in Streamlit
    st.markdown(clock_html, unsafe_allow_html=True)

if __name__ == "__main__":
    clock_main()
