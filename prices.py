from datetime import datetime, timedelta
import math

#This file is used to explain the prices calculation as every single parkhaus is different 

#Function that return the parking, based on nearest parking space 
def calculate_parking_fees(parking_name, arrival_datetime, duration_hours):
    if parking_name == "Manor":
        return calculate_fee_manor(arrival_datetime, duration_hours)
    elif parking_name == "Bahnhof":
        return calculate_fee_bahnhof(arrival_datetime, duration_hours)
    elif parking_name == "Brühltor":
        return calculate_fee_brühltor(arrival_datetime, duration_hours)
    elif parking_name == "Burggraben":
        return calculate_fee_burggraben(arrival_datetime, duration_hours)
    elif parking_name == "Stadtpark AZSG":
        return calculate_fee_stadtpark_azsg(arrival_datetime, duration_hours)
    elif parking_name == "Neumarkt":
        return calculate_fee_neumarkt(arrival_datetime, duration_hours)
    elif parking_name == "Rathaus":
        return calculate_fee_rathaus(arrival_datetime, duration_hours)
    elif parking_name == "Kreuzbleiche":
        return calculate_fee_kreuzbleiche(arrival_datetime, duration_hours)
    elif parking_name == "Oberer Graben":
        return calculate_fee_oberer_graben(arrival_datetime, duration_hours)
    elif parking_name == "Raiffeisen":
        return calculate_fee_raiffeisen(arrival_datetime, duration_hours)
    elif parking_name == "Einstein":
        return calculate_fee_einstein(arrival_datetime, duration_hours)
    elif parking_name == "Spisertor":
        return calculate_fee_spisertor(arrival_datetime, duration_hours)
    elif parking_name == "Spelterini":
        return calculate_fee_spelterini(arrival_datetime, duration_hours)
    elif parking_name == "OLMA Messe":
        return calculate_fee_olma_messe(arrival_datetime, duration_hours)
    elif parking_name == "Unterer Graben":
        return calculate_fee_unterer_graben(arrival_datetime, duration_hours)
    elif parking_name == "OLMA Parkplatz":
        return calculate_fee_olma_parkplatz(arrival_datetime, duration_hours)       
    else:
        return "Parking name not recognized. Please check the parking name."
    
#Calculation for every single parking space
#standard identification--> def "name parking"(arrival_datetime, duration_hours)

def calculate_fee_manor(arrival_datetime, duration_hours):
    # Definizione dei limiti temporali per la tariffa notturna
    night_start = 21.5   # 21:30 PM
    night_end = 0.5      # 00:30 AM, tecnicamente il giorno seguente
    
    # Tariffe diurne dettagliate
    rates = [
        (1, 2.00),                    # Tariffa per la prima ora
        (2, 1.00 / 3),                # Tariffa per da 1 a 3 ore
        (None, 1.50 / 3)              # Tariffa oltre le 3 ore
    ]

    total_fee = 0
    current_time = arrival_datetime
    hours_processed = 0

    while hours_processed < duration_hours:
        current_hour = current_time.hour + current_time.minute / 60

        if night_start <= current_hour or current_hour < night_end:
            # Calcolo delle tariffe notturne
            if current_hour >= night_start:
                hours_to_charge = min(duration_hours - hours_processed, 24 - current_hour + night_end)
            else:
                hours_to_charge = min(duration_hours - hours_processed, night_end - current_hour)

            segments = hours_to_charge * 2  # Segmenti di 30 minuti
            total_fee += segments * 1.00  # 1 CHF ogni 30 minuti
            hours_processed += hours_to_charge
            current_time += timedelta(hours=hours_to_charge)
        else:
            # Calcolo delle tariffe diurne
            for hours, rate in rates:
                if hours is None or hours_processed + hours > duration_hours:
                    hours = duration_hours - hours_processed

                segments = hours * 3  # Segmenti di 20 minuti
                total_fee += segments * rate
                hours_processed += hours
                current_time += timedelta(hours=hours)

    return math.ceil(total_fee)  # Arrotonda per eccesso il costo totale


def calculate_fee_bahnhof(arrival_datetime, duration_hours):
    daytime_rates = [
        (1, 2.40),  # First hour at 2.40 CHF from 6 AM to 10 PM
        (None, 1.20, 0.5)  # Beyond the first hour, 1.20 CHF per 30 minutes
    ]
    nighttime_rates = [
        (1, 1.20),  # First hour at 1.20 CHF from 10 PM to 6 AM
        (None, 0.60, 0.5)  # Beyond the first hour, 0.60 CHF per 30 minutes
    ]

    total_fee = 0
    current_hour = arrival_datetime.hour + arrival_datetime.minute / 60
    hours_left = duration_hours

    while hours_left > 0:
        # Determine if current hour is during day or night rates
        if 6 <= current_hour < 22:
            # Daytime rates
            for duration, rate, interval in daytime_rates:
                if duration is None or hours_left < duration:
                    hours_to_charge = min(hours_left, interval)
                    total_fee += math.ceil(hours_to_charge / interval) * rate
                    hours_left -= hours_to_charge
                    current_hour += hours_to_charge
                    break
                else:
                    total_fee += rate
                    hours_left -= duration
                    current_hour += duration
        else:
            # Nighttime rates
            for duration, rate, interval in nighttime_rates:
                if duration is None or hours_left < duration:
                    hours_to_charge = min(hours_left, interval)
                    total_fee += math.ceil(hours_to_charge / interval) * rate
                    hours_left -= hours_to_charge
                    current_hour += hours_to_charge
                    break
                else:
                    total_fee += rate
                    hours_left -= duration
                    current_hour += duration

        current_hour = current_hour % 24  # Reset the hour after midnight

    return f"Total parking fee at Bahnhof: {math.ceil(total_fee)} CHF"

def calculate_fee_brühltor(arrival_datetime, duration_hours):
    # Defining rate details for Brühltor
    rates = {
        "day": [(1, 2.00, 1), (None, 1.00, 0.5)],  # After 1st hour, charge per 30 minutes
        "night": [(1, 1.20, 1), (None, 0.60, 0.5)]  # Night rates
    }
    valid_hours = {"day": (7, 24), "night": (0, 7)}  # Operating hours

    total_fee = 0
    current_time = arrival_datetime
    hours_left = duration_hours

    while hours_left > 0:
        current_hour = current_time.hour + current_time.minute / 60

        # Determine if it's day or night for rate application
        if valid_hours["day"][0] <= current_hour < valid_hours["day"][1]:
            rate_info = rates["day"]
        else:
            rate_info = rates["night"]

        # Apply rates based on the current time period
        for hours, rate, interval in rate_info:
            if hours is None or duration_hours < hours:
                hours_to_charge = min(duration_hours, interval)
                total_fee += (hours_to_charge / interval) * rate
                duration_hours -= hours_to_charge
                current_time += timedelta(hours=hours_to_charge)
            elif duration_hours >= hours:
                total_fee += rate
                duration_hours -= hours
                current_time += timedelta(hours=hours)

        # Handle day-night transition and ensure time updates correctly
        current_time = (current_time.hour % 24) + timedelta(minutes=current_time.minute)

    # Return total fee, rounding up to the nearest franc
    return f"Total parking fee at Brühltor: {math.ceil(total_fee):.2f} CHF"


def calculate_fee_burggraben(arrival_datetime, duration_hours):
    # Rates and times definitions
    daytime_rates = [
        (1, 2.00),  # First hour at 2.00 CHF
        (None, 1.00, 0.5)  # Beyond first hour, 1.00 CHF per 30 minutes
    ]
    nighttime_rates = [
        (1, 1.20),  # First hour at 1.20 CHF
        (None, 0.60, 0.5)  # Beyond first hour, 0.60 CHF per 30 minutes
    ]
    weekend_rates = [
        (1, 2.40),  # First hour at 2.40 CHF
        (None, 1.20, 0.5)  # Beyond first hour, 1.20 CHF per 30 minutes
    ]
    valid_hours = {"day": (7, 24), "night": (0, 7)}

    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    total_fee = 0
    hours_left = duration_hours
    is_weekend = arrival_datetime.weekday() >= 5  # 5 for Saturday, 6 for Sunday

    # Determine rate details based on weekend
    rate_details = weekend_rates if is_weekend else daytime_rates if 7 <= current_time < 24 else nighttime_rates

    while hours_left > 0:
        for (hours, rate, interval) in rate_details:
            if hours is None or hours_left < hours:
                hours_to_charge = min(hours_left, interval if interval else hours)
                total_fee += (hours_to_charge / interval if interval else hours_to_charge) * rate
                hours_left -= hours_to_charge
                current_time += hours_to_charge
                break
            else:
                total_fee += rate
                hours_left -= hours

        # Update rate details based on time after processing current rates
        current_time = (current_time % 24)  # Reset the time after midnight
        if 7 <= current_time < 24:
            rate_details = weekend_rates if is_weekend else daytime_rates
        else:
            rate_details = nighttime_rates

    return f"Total parking fee at Burggraben: {total_fee:.2f} CHF"


def calculate_fee_stadtpark_azsg(arrival_datetime, duration_hours):
    # Define the parking rates and hours
    standard_rates = {
        "event": [(1, 2.40), (None, 1.20, 0.5)],
        "day": [(1, 1.60), (None, 0.80, 0.5)],
        "night": [(1, 0.80), (None, 0.40, 0.5)]
    }
    event_days = [5]  # Assuming events occur on Saturdays (day index 5)
    valid_hours = {"day": (7, 24), "night": (0, 7)}
    daily_rates = [(24, 18), (48, 36), (72, 54)]  # Flat rates for full day durations

    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    total_fee = 0
    hours_left = duration_hours

    # Check if it's an event day
    is_event_day = arrival_datetime.weekday() in event_days

    # Apply daily flat rates if parking duration covers full days
    for duration, rate in daily_rates:
        if hours_left >= duration:
            total_fee += rate
            hours_left -= duration

    # Calculate hourly rates for the remaining time
    while hours_left > 0:
        if valid_hours["day"][0] <= current_time < valid_hours["day"][1]:
            # Daytime rates
            rate_details = standard_rates["event"] if is_event_day else standard_rates["day"]
            for (hours, rate, interval) in rate_details:
                if hours is None or hours_left <= hours:
                    hours_to_charge = min(hours_left, interval)
                    total_fee += hours_to_charge * rate
                    hours_left -= hours_to_charge
                    current_time += hours_to_charge
                    break
        else:
            # Nighttime rates
            for (hours, rate, interval) in standard_rates["night"]:
                if hours is None or hours_left <= hours:
                    hours_to_charge = min(hours_left, interval)
                    total_fee += hours_to_charge * rate
                    hours_left -= hours_to_charge
                    current_time += hours_to_charge
                    break

        current_time = (current_time % 24)  # Reset the time after midnight

    return f"Total parking fee at Stadtpark AZSG: {total_fee:.2f} CHF"

def calculate_fee_neumarkt(arrival_datetime, duration_hours):
    flat_rate = 1  # CHF per hour

    # Total fee is simply the flat rate multiplied by the duration in hours, rounded up
    total_fee = math.ceil(duration_hours) * flat_rate

    return f"Total parking fee at Neumarkt: {total_fee:.2f} CHF"

def calculate_fee_rathaus(arrival_datetime, duration_hours):
    daytime_hours = (7, 22)  # From 7 AM to 10 PM
    night_rate = 1.2  # CHF per hour at night
    day_rate = 2.4  # CHF per hour during the day

    total_fee = 0.0
    current_time = arrival_datetime.hour + arrival_datetime.minute / 60

    hours_left = duration_hours

    while hours_left > 0:
        if daytime_hours[0] <= current_time < daytime_hours[1]:
            # Calculate daytime fee
            day_hours_left = min(daytime_hours[1] - current_time, hours_left)
            total_fee += math.ceil(day_hours_left) * day_rate  # Round up the hours to charge
            hours_left -= day_hours_left
            current_time += day_hours_left
        else:
            # Calculate nighttime fee
            if current_time >= daytime_hours[1]:
                night_hours_left = 24 - current_time
            else:
                night_hours_left = daytime_hours[0] - current_time

            night_hours_left = min(night_hours_left, hours_left)
            total_fee += math.ceil(night_hours_left) * night_rate  # Round up the hours to charge
            hours_left -= night_hours_left
            current_time += night_hours_left

        current_time %= 24  # Reset time after midnight

    return f"Total parking fee at Rathaus: {total_fee:.2f} CHF"

def calculate_fee_kreuzbleiche(arrival_datetime, duration_hours):
    daytime_hours = (7, 22)  # Daytime from 7 AM to 10 PM
    night_rate = 1.0  # CHF per hour during the night
    day_rate = 1.5  # CHF per hour during the day

    total_fee = 0.0
    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    hours_left = duration_hours

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

    return f"Total parking fee at Kreuzbleiche: {total_fee:.2f} CHF"

def calculate_fee_oberer_graben(arrival_datetime, duration_hours):
    daytime_hours = (6, 23)  # Daytime from 6 AM to 11 PM
    night_rate = 1.5  # CHF per hour during the night
    day_rate = 2.0  # CHF per hour during the day

    total_fee = 0.0
    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    hours_left = duration_hours

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

    return f"Total parking fee at Oberer Graben: {total_fee:.2f} CHF"
    
def calculate_fee_raiffeisen(arrival_datetime, duration_hours):
    initial_rate_hours = 3  # The first three hours have a different rate
    subsequent_rate = 1.5  # CHF per each additional hour after the first three hours
    initial_rate = 2  # CHF for the first three hours

    total_fee = 0.0
    if duration_hours <= initial_rate_hours:
        total_fee = initial_rate * duration_hours
    else:
        total_fee += initial_rate_hours * initial_rate  # Charge for the first three hours
        remaining_hours = duration_hours - initial_rate_hours
        total_fee += remaining_hours * subsequent_rate  # Charge for the remaining hours

    return f"Total parking fee at Raiffeisen: {total_fee:.2f} CHF"

def calculate_fee_einstein(arrival_datetime, duration_hours):
    flat_rate = 2.5  # CHF per hour regardless of duration

    total_fee = flat_rate * duration_hours  # Total fee is simply the hourly rate multiplied by hours parked

    return f"Total parking fee at Einstein: {total_fee:.2f} CHF"

def calculate_fee_spisertor(arrival_datetime, duration_hours):
    flat_rate = 2.5  # CHF per hour regardless of duration

    total_fee = flat_rate * duration_hours  # Total fee is simply the hourly rate multiplied by hours parked

    return f"Total parking fee at Spisertor: {total_fee:.2f} CHF"

def calculate_fee_spelterini(arrival_datetime, duration_hours):
    daytime_start = 7  # Daytime starts at 7 AM
    daytime_end = 24  # Daytime ends at midnight
    extended_rate_hours = 3  # First three hours
    extended_rate = 2  # CHF for the first three hours
    extended_increment = 1.5  # CHF per hour after the first three hours
    night_rate = 0.6  # Night rate per hour
    
    current_hour = arrival_datetime.hour + arrival_datetime.minute / 60
    total_fee = 0
    hours_processed = 0

    # Calculate for the first three hours or less
    hours_at_extended_rate = min(duration_hours, extended_rate_hours)
    total_fee += hours_at_extended_rate * extended_rate
    hours_processed += hours_at_extended_rate

    # Calculate for additional hours at extended increment rate
    if duration_hours > extended_rate_hours:
        additional_hours = duration_hours - extended_rate_hours
        total_fee += additional_hours * extended_increment
        hours_processed += additional_hours

    # Calculate for any night rate if applicable
    if current_hour + hours_processed >= daytime_end:
        hours_at_night_rate = current_hour + hours_processed - daytime_end
        if hours_at_night_rate > 0:
            total_fee += hours_at_night_rate * night_rate

    return f"Total parking fee at Spelterini: {total_fee:.2f} CHF"


def calculate_fee_olma_messe(arrival_datetime, duration_hours):
    total_fee = 0
    current_hour = arrival_datetime.hour + arrival_datetime.minute / 60
    base_hours = 3
    base_rate = 2
    incremental_rate = 1.5
    rate_interval = 1  # Rate changes every hour after the first three hours

    if duration_hours <= base_hours:
        total_fee = base_rate * duration_hours
    else:
        total_fee = base_rate * base_hours
        additional_hours = duration_hours - base_hours
        while additional_hours > 0:
            hours_to_charge = min(additional_hours, rate_interval)
            total_fee += incremental_rate * hours_to_charge
            additional_hours -= hours_to_charge

    return f"Total parking fee at OLMA Messe: {total_fee:.2f} CHF"

def calculate_fee_unterer_graben(arrival_datetime, duration_hours):
    flat_rate = 2  # Flat rate per hour
    total_fee = flat_rate * duration_hours

    return f"Total parking fee at Unterer Graben: {total_fee:.2f} CHF"
def calculate_fee_olma_parkplatz(arrival_datetime, duration_hours):
    daytime_start = 6  # Daytime starts at 6 AM
    nighttime_start = 23  # Nighttime starts at 11 PM
    day_rate = 2  # Day rate per hour
    night_rate = 1.5  # Night rate per hour
    total_fee = 0
    current_hour = arrival_datetime.hour + arrival_datetime.minute / 60

    for _ in range(int(duration_hours)):
        if daytime_start <= current_hour < nighttime_start:
            total_fee += day_rate
        else:
            total_fee += night_rate
        current_hour = (current_hour + 1) % 24  # Wrap around to the next hour, mod 24 for midnight wrap-around

    return f"Total parking fee at OLMA Parkplatz: {total_fee:.2f} CHF"




