import streamlit as st

def clock_main():
     
    # Clock HTML and inline CSS/JS
    clock_html = """
    <div style="width: 200px; height: 200px; background: #fff; border-radius: 50%; border: 10px solid #333; display: flex; justify-content: center; align-items: center; position: relative;">
        <div style="position: absolute; width: 8px; height: 50px; background: black; transform-origin: bottom; transform: rotate(-90deg);" id="hour_hand"></div>
        <div style="position: absolute; width: 4px; height: 80px; background: black; transform-origin: bottom; transform: rotate(-90deg);" id="minute_hand"></div>
        <div style="position: absolute; width: 2px; height: 90px; background: red; transform-origin: bottom; transform: rotate(-90deg);" id="second_hand"></div>
        <div style="width: 12px; height: 12px; background: black; border-radius: 50%;"></div>
    </div>
    <script>
        function updateHands() {
            const now = new Date();
            const seconds = now.getSeconds();
            const minutes = now.getMinutes();
            const hours = now.getHours();
            
            const secondsAngle = seconds * 6;  // 360/60
            const minutesAngle = minutes * 6 + seconds * 0.1;  // 360/60 + partial minute
            const hoursAngle = (hours % 12) * 30 + minutes * 0.5;  // 360/12 + partial hour

            document.getElementById('second_hand').style.transform = 'rotate(' + (secondsAngle - 90) + 'deg)';
            document.getElementById('minute_hand').style.transform = 'rotate(' + (minutesAngle - 90) + 'deg)';
            document.getElementById('hour_hand').style.transform = 'rotate(' + (hoursAngle - 90) + 'deg)';
        }

        setInterval(updateHands, 1000);
        updateHands(); // Initial call to set the hands correctly
    </script>
    """
    
    # Display the HTML clock in Streamlit
    st.markdown(clock_html, unsafe_allow_html=True)

if __name__ == "__main__":
    clock_main()

