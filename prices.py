from datetime import datetime, timedelta
import math

#This file is used to explain the prices calculation as every single parkhaus is different 

def calculate_parking_fees(parking_name, arrival_datetime, rounded_total_hours):
    if parking_name == "Manor":
        return calculate_fee_manor(arrival_datetime, rounded_total_hours)
    elif parking_name == "Bahnhof":
        return calculate_fee_bahnhof(arrival_datetime, rounded_total_hours)
    elif parking_name == "Brühltor":
        return calculate_fee_brühltor(arrival_datetime, rounded_total_hours)
    elif parking_name == "Burggraben":
        return calculate_fee_burggraben(arrival_datetime, rounded_total_hours)
    elif parking_name == "Stadtpark AZSG":
        return calculate_fee_stadtpark_azsg(arrival_datetime, rounded_total_hours)
    elif parking_name == "Neumarkt":
        return calculate_fee_neumarkt(arrival_datetime, rounded_total_hours)
    elif parking_name == "Rathaus":
        return calculate_fee_rathaus(arrival_datetime, rounded_total_hours)
    elif parking_name == "Kreuzbleiche":
        return calculate_fee_kreuzbleiche(arrival_datetime, rounded_total_hours)
    elif parking_name == "Oberer Graben":
        return calculate_fee_oberer_graben(arrival_datetime, rounded_total_hours)
    elif parking_name == "Raiffeisen":
        return calculate_fee_raiffeisen(arrival_datetime, rounded_total_hours)
    elif parking_name == "Einstein":
        return calculate_fee_einstein(arrival_datetime, rounded_total_hours)
    elif parking_name == "Spisertor":
        return calculate_fee_spisertor(arrival_datetime, rounded_total_hours)
    elif parking_name == "Spelterini":
        return calculate_fee_spelterini(arrival_datetime, rounded_total_hours)
    elif parking_name == "OLMA Messe":
        return calculate_fee_olma_messe(arrival_datetime, rounded_total_hours)
    elif parking_name == "Unterer Graben":
        return calculate_fee_unterer_graben(arrival_datetime, rounded_total_hours)
    elif parking_name == "OLMA Parkplatz":
        return calculate_fee_olma_parkplatz(arrival_datetime, rounded_total_hours)
    else:
        return "Parking name not recognized. Please check the parking name."

    
#Calculation for every single parking space
#standard identification--> def "name parking"(arrival_datetime, duration_hours)

def calculate_fee_manor(arrival_datetime, rounded_total_hours):
    initial_rate = 2.0  # CHF for less than 1 hour
    mid_rate = 3.0  # CHF per hour for 1 to 3 hours
    long_term_rate = 4.5  # CHF per hour for more than 3 hours

    # Initialize the total fee
    total_fee = 0.0

    # Apply the rate based on the rounded_total_hours
    if rounded_total_hours <= 1:
        total_fee = initial_rate  # Apply initial rate if parking duration is less than 1 hour
    elif rounded_total_hours <= 3:
        total_fee = mid_rate * rounded_total_hours  # Apply mid rate if parking duration is between 1 and 3 hours
    else:
        total_fee = long_term_rate * rounded_total_hours  # Apply long term rate if parking duration is more than 3 hours

    return f" at Manor: {total_fee:.2f} CHF"


def calculate_fee_bahnhof(arrival_datetime, rounded_total_hours):
    daytime_rate_first_hour = 2.40
    day_subsequent_rate = 1.20
    nighttime_rate_first_hour = 1.20
    night_subsequent_rate = 0.60

    total_fee = 0.0
    current_time = arrival_datetime
    remaining_hours = rounded_total_hours

    while remaining_hours > 0:
        current_hour = current_time.hour + current_time.minute / 60

        if 6 <= current_hour < 22:
            if total_fee == 0:  # First hour
                total_fee += daytime_rate_first_hour
                remaining_hours -= 1
            else:
                total_fee += day_subsequent_rate
                remaining_hours -= 0.5
        else:
            if total_fee == 0:  # First hour
                total_fee += nighttime_rate_first_hour
                remaining_hours -= 1
            else:
                total_fee += night_subsequent_rate
                remaining_hours -= 0.5

        current_time += timedelta(minutes=30)

    return f"at Bahnhof: {total_fee:.2f} CHF"




def calculate_fee_brühltor(arrival_datetime, rounded_total_hours):
    daytime_rate = 2.00  # CHF for the first hour
    day_subsequent_rate = 1.00  # CHF per 30 minutes after the first hour
    nighttime_rate = 1.20  # CHF for the first hour at night
    night_subsequent_rate = 0.60  # CHF per 30 minutes after the first hour at night

    total_fee = 0.0
    current_hour = arrival_datetime.hour + arrival_datetime.minute / 60

    # Correct time ranges for day and night
    if 7 <= current_hour < 22:  # Daytime fees calculation
        if rounded_total_hours <= 1:
            total_fee += daytime_rate
        else:
            total_fee += daytime_rate  # First hour
            additional_hours = rounded_total_hours - 1
            # Calculate for each 30 minutes interval after the first hour
            total_fee += (additional_hours * 2) * day_subsequent_rate / 2
    else:  # Nighttime fees calculation
        if rounded_total_hours <= 1:
            total_fee += nighttime_rate
        else:
            total_fee += nighttime_rate  # First hour
            additional_hours = rounded_total_hours - 1
            # Calculate for each 30 minutes interval after the first hour
            total_fee += (additional_hours * 2) * night_subsequent_rate / 2

    return f" at Brühltor: {(total_fee):.2f} CHF"



def calculate_fee_burggraben(arrival_datetime, rounded_total_hours):
    daytime_rate = 2.00  # CHF for the first hour
    day_subsequent_rate = 1.00  # CHF per 30 minutes after the first hour
    nighttime_rate = 1.20  # CHF for the first hour at night
    night_subsequent_rate = 0.60  # CHF per 30 minutes after the first hour at night

    total_fee = 0.0
    current_hour = arrival_datetime.hour + arrival_datetime.minute / 60

    # Calculate daytime fees if within daytime hours
    if 6 <= current_hour < 22:
        if rounded_total_hours <= 1:
            total_fee += daytime_rate
        else:
            total_fee += daytime_rate  # First hour
            additional_hours = rounded_total_hours-1
            total_fee += math.ceil(additional_hours * 2) * (day_subsequent_rate)  # Subsequent rates per 30 minutes
    else:  # Calculate nighttime fees
        if rounded_total_hours <= 1:
            total_fee += nighttime_rate
        else:
            total_fee += nighttime_rate  # First hour
            additional_hours = rounded_total_hours - 1
            total_fee += math.ceil(additional_hours * 2) * (night_subsequent_rate / 2)  # Subsequent rates per 30 minutes

    return f" at Burggraben: {(total_fee):.2f} CHF"

def calculate_fee_stadtpark_azsg(arrival_datetime, rounded_total_hours):
    daytime_rate = 1.60  # CHF for the first hour
    day_subsequent_rate = 0.80  # CHF per 30 minutes after the first hour
    nighttime_rate = 0.80  # CHF for the first hour at night
    night_subsequent_rate = 0.40  # CHF per 30 minutes after the first hour at night

    total_fee = 0.0
    current_time = arrival_datetime

    # Define daytime and nighttime hours
    daytime_start = 7
    nighttime_start = 24

    # Calculate the number of 30-minute intervals
    total_half_hours = math.ceil(rounded_total_hours * 2)
    is_first_hour = True

    for _ in range(total_half_hours):  # Loop over each half-hour segment
        current_hour = current_time.hour + current_time.minute / 60
        
        if daytime_start <= current_hour < nighttime_start:
            if is_first_hour:
                total_fee += daytime_rate  # Charge for the first hour
                is_first_hour = False
            else:
                total_fee += day_subsequent_rate  # Charge for each 30 minutes after the first hour
        else:
            if is_first_hour:
                total_fee += nighttime_rate  # Charge for the first hour
                is_first_hour = False
            else:
                total_fee += night_subsequent_rate  # Charge for each 30 minutes after the first hour

        current_time += timedelta(minutes=30)

    return f"at Stadtpark AZSG: {total_fee:.2f} CHF"

def calculate_fee_neumarkt(arrival_datetime, rounded_total_hours):
    day_rate = 3.0  # CHF per hour during the day (7 AM to 10 PM)
    night_rate = 2.0  # CHF per hour during the night (10 PM to 7 AM)
    daytime_hours = (7, 22)  # From 7 AM to 10 PM

    total_fee = 0.0
    current_time = arrival_datetime
    hours_left = rounded_total_hours

    while hours_left > 0:
        current_hour = current_time.hour + current_time.minute / 60

        if daytime_hours[0] <= current_hour < daytime_hours[1]:
            # Calculate daytime fee
            if hours_left + current_hour > daytime_hours[1]:
                hours_to_charge = daytime_hours[1] - current_hour
            else:
                hours_to_charge = hours_left
            total_fee += hours_to_charge * day_rate
            hours_left -= hours_to_charge
            current_time = current_time.replace(hour=int((current_time.hour + hours_to_charge) % 24))
        else:
            # Calculate nighttime fee
            if current_hour >= daytime_hours[1]:
                hours_to_charge = min(hours_left, 24 - current_hour)
            else:
                hours_to_charge = min(hours_left, daytime_hours[0] - current_hour)
            total_fee += hours_to_charge * night_rate
            hours_left -= hours_to_charge
            current_time = current_time.replace(hour=int((current_time.hour + hours_to_charge) % 24))

    return f" at Neumarkt: {total_fee:.2f} CHF"


def calculate_fee_rathaus(arrival_datetime, rounded_total_hours):
    daytime_hours = (7, 22)  # From 7 AM to 10 PM
    night_rate = 1.2  # CHF per hour at night
    day_rate = 2.4  # CHF per hour during the day

    total_fee = 0.0
    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    hours_left = rounded_total_hours

    while hours_left > 0:
        if daytime_hours[0] <= current_time < daytime_hours[1]:
            # Calculate daytime fee
            day_hours_left = min(daytime_hours[1] - current_time, hours_left)
            total_fee += math.ceil(day_hours_left) * day_rate  # Apply day rate and round up
            hours_left -= day_hours_left
            current_time += day_hours_left
        else:
            # Calculate nighttime fee
            if current_time >= daytime_hours[1]:
                night_hours_left = 24 - current_time
            else:
                night_hours_left = daytime_hours[0] - current_time

            night_hours_left = min(night_hours_left, hours_left)
            total_fee += math.ceil(night_hours_left) * night_rate  # Apply night rate and round up
            hours_left -= night_hours_left
            current_time += night_hours_left

        current_time %= 24  # Reset time after midnight

    return f" at Rathaus: {total_fee:.2f} CHF"

def calculate_fee_kreuzbleiche(arrival_datetime, rounded_total_hours):
    daytime_hours = (6, 23)  # Daytime from 6 AM to 11 PM
    night_rate = 1.0  # CHF per hour during the night
    day_rate = 1.5  # CHF per hour during the day

    total_fee = 0.0
    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    hours_left = rounded_total_hours

    while hours_left > 0:
        if daytime_hours[0] <= current_time < daytime_hours[1]:
            # Calculate daytime fee
            day_hours_left = min(daytime_hours[1] - current_time, hours_left)
            total_fee += day_hours_left * day_rate
            hours_left -= day_hours_left
            current_time += day_hours_left
        else:
            # Calculate nighttime fee
            if current_time >= daytime_hours[1]:
                night_hours_left = 24 - current_time
            else:
                night_hours_left = daytime_hours[0] - current_time

            night_hours_left = min(night_hours_left, hours_left)
            total_fee += night_hours_left * night_rate
            hours_left -= night_hours_left
            current_time += night_hours_left

        current_time %= 24  # Reset time after midnight

    # Round the total fee to the nearest whole number
    total_fee = (total_fee)

    return f"at Kreuzbleiche: {total_fee:.2f} CHF"

def calculate_fee_oberer_graben(arrival_datetime, rounded_total_hours):
    daytime_hours = (6, 23)  # Daytime from 6 AM to 11 PM
    night_rate = 1.5  # CHF per hour during the night
    day_rate = 2.0  # CHF per hour during the day

    total_fee = 0.0
    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    hours_left = rounded_total_hours

    while hours_left > 0:
        if daytime_hours[0] <= current_time < daytime_hours[1]:
            # Calculate daytime fee
            day_hours_left = min(daytime_hours[1] - current_time, hours_left)
            total_fee += day_hours_left * day_rate
            hours_left -= day_hours_left
            current_time += day_hours_left
        else:
            # Calculate nighttime fee
            if current_time >= daytime_hours[1]:
                night_hours_left = 24 - current_time
            else:
                night_hours_left = daytime_hours[0] - current_time

            night_hours_left = min(night_hours_left, hours_left)
            total_fee += night_hours_left * night_rate
            hours_left -= night_hours_left
            current_time += night_hours_left

        current_time %= 24  # Reset time after midnight

    # Round the total fee to the nearest whole number
    total_fee = math.ceil(total_fee)

    return f" at Oberer Graben: {total_fee:.2f} CHF"
    
def calculate_fee_raiffeisen(arrival_datetime, rounded_total_hours):
    initial_rate = 2.0  # CHF per hour for the first 3 hours
    mid_rate = 1.5  # CHF per hour from 3 to 13 hours
    long_term_rate = 1.0  # CHF per hour beyond 13 hours
    first_rate_hours = 3  # Duration for the initial rate
    mid_rate_limit = 13  # Upper limit for the mid rate

    total_fee = 0.0

    # Apply the rate based on the rounded_total_hours
    if rounded_total_hours <= first_rate_hours:
        total_fee = rounded_total_hours * initial_rate
    elif rounded_total_hours <= mid_rate_limit:
        total_fee = rounded_total_hours * mid_rate
    else:
        total_fee = rounded_total_hours * long_term_rate

    return f" at Raiffeisen: {total_fee:.2f} CHF"


def calculate_fee_einstein(arrival_datetime, rounded_total_hours):
    flat_rate = 2.5  # CHF per hour regardless of duration

    total_fee = flat_rate * rounded_total_hours  # Total fee is simply the hourly rate multiplied by hours parked

    return f" at Einstein: {total_fee:.2f} CHF"

def calculate_fee_spisertor(arrival_datetime, rounded_total_hours):
    flat_rate = 2.5  # CHF per hour
    max_daily_rate = 30  # CHF per day

    # Calculate the total number of complete 24-hour periods
    complete_days = rounded_total_hours // 24
    remaining_hours = rounded_total_hours % 24

    # Calculate the fee for the complete 24-hour periods
    total_fee = complete_days * max_daily_rate

    # Calculate the fee for the remaining hours
    remaining_fee = min(flat_rate * remaining_hours, max_daily_rate)
    total_fee += remaining_fee

    return f" at Spisertor: {total_fee:.2f} CHF"

def calculate_fee_spelterini(arrival_datetime, rounded_total_hours):
    daytime_hours = (7, 24)  # Daytime from 6 AM to 11 PM
    night_rate = 1.5  # CHF per hour during the night
    day_rate = 2.0  # CHF per hour during the day

    total_fee = 0.0
    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    hours_left = rounded_total_hours

    while hours_left > 0:
        if daytime_hours[0] <= current_time < daytime_hours[1]:
            # Calculate daytime fee
            day_hours_left = min(daytime_hours[1] - current_time, hours_left)
            total_fee += day_hours_left * day_rate
            hours_left -= day_hours_left
            current_time += day_hours_left
        else:
            # Calculate nighttime fee
            if current_time >= daytime_hours[1]:
                night_hours_left = 24 - current_time
            else:
                night_hours_left = daytime_hours[0] - current_time

            night_hours_left = min(night_hours_left, hours_left)
            total_fee += night_hours_left * night_rate
            hours_left -= night_hours_left
            current_time += night_hours_left

        current_time %= 24  # Reset time after midnight

    # Round the total fee to the nearest whole number
    total_fee = (total_fee)
    return f" at Spelterini: {total_fee:.2f} CHF"


def calculate_fee_olma_messe(arrival_datetime, rounded_total_hours):
    total_fee = 0
    current_hour = arrival_datetime.hour + arrival_datetime.minute / 60
    base_hours = 3
    base_rate = 2
    incremental_rate = 1.5
    rate_interval = 1  # Rate changes every hour after the first three hours

    if rounded_total_hours <= base_hours:
        total_fee = base_rate * rounded_total_hours
    else:
        total_fee = base_rate * base_hours
        additional_hours = rounded_total_hours - base_hours
        while additional_hours > 0:
            hours_to_charge = min(additional_hours, rate_interval)
            total_fee += incremental_rate * hours_to_charge
            additional_hours -= hours_to_charge

    return f" at OLMA Messe: {total_fee:.2f} CHF"

def calculate_fee_unterer_graben(arrival_datetime, rounded_total_hours):
    flat_rate = 2  # Flat rate per hour
    total_fee = flat_rate * rounded_total_hours

    return f"at Unterer Graben: {total_fee:.2f} CHF"

def calculate_fee_olma_parkplatz(arrival_datetime, rounded_total_hours):
    daytime_start = 6  # Daytime starts at 6 AM
    nighttime_start = 23  # Nighttime starts at 11 PM
    day_rate = 2  # Day rate per hour
    night_rate = 1.5  # Night rate per hour
    total_fee = 0
    current_hour = arrival_datetime.hour + arrival_datetime.minute / 60

    for _ in range(int(rounded_total_hours)):  # Adjust to use rounded_total_hours
        if daytime_start <= current_hour < nighttime_start:
            total_fee += day_rate
        else:
            total_fee += night_rate
        current_hour = (current_hour + 1) % 24  # Wrap around to the next hour, mod 24 for midnight wrap-around

    return f" at OLMA Parkplatz: {total_fee:.2f} CHF"




