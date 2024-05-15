from datetime import datetime, timedelta
import math

def calculate_parking_fees(parking_name, arrival_datetime, duration_hours):
    if parking_name == "Manor":
        return calculate_fee_manor(arrival_datetime, duration_hours)
    elif parking_name == "Bahnhof":
        return calculate_fee_bahnhof(arrival_datetime, duration_hours)
    elif parking_name == "Brühltor":
        return calculate_fee_bruehltor(arrival_datetime, duration_hours)
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
    
def calculate_fee_manor(arrival_datetime, duration_hours):
    daytime_start = 5.5  # 5:30 AM
    daytime_end = 21  # 9:00 PM
    night_rate = 1  # CHF per hour at night
    rates = [(1, 2), (3, 1, 20), (None, 1.5, 20)]  # Rates as (hours, rate, interval in minutes)

    total_fee = 0
    current_time = arrival_datetime

    while duration_hours > 0:
        current_hour = current_time.hour + current_time.minute / 60

        if daytime_start <= current_hour < daytime_end:
            # Daytime rate calculations
            for rate_detail in rates:
                if len(rate_detail) == 3:
                    hours, rate, interval = rate_detail
                elif len(rate_detail) == 2:
                    hours, rate = rate_detail
                    interval = 60  # Default interval to 60 minutes if not specified

                if hours is None or duration_hours < hours:
                    minutes_to_charge = min(duration_hours * 60, interval)  # Convert hours to minutes or use the specified interval
                    intervals_count = int(minutes_to_charge / interval)
                    total_fee += intervals_count * rate
                    minutes_to_charge -= intervals_count * interval
                    duration_hours -= intervals_count * (interval / 60)  # Convert minutes back to hours
                    break
                elif duration_hours >= hours:
                    total_fee += rate
                    duration_hours -= hours

        else:
            # Nighttime rate calculation
            if current_hour >= daytime_end:
                hours_to_midnight = 24 - current_hour
                time_till_day = hours_to_midnight + daytime_start
            else:
                time_till_day = daytime_start - current_hour

            if duration_hours < time_till_day:
                total_fee += duration_hours * night_rate
                duration_hours = 0
            else:
                total_fee += time_till_day * night_rate
                duration_hours -= time_till_day

        current_time += timedelta(hours=duration_hours)  # Update current time

    return total_fee



def calculate_fee_bahnhof(arrival_datetime, duration_hours):
    # Rates for various durations at Bahnhof
    rates = [
        (0.1667, 0),  # Free for up to 10 minutes
        (0.3333, 0.50),  # 11 to 20 minutes at 0.50 CHF
        (0.5, 1.50),  # 21 to 30 minutes at 1.50 CHF
        (1, 3.00),  # First hour at 3.00 CHF
        (None, 2.00, 0.5)  # Beyond first hour, 2.00 CHF per 30 minutes
    ]
    daily_rates = [(1, 25), (2, 50), (3, 75)]  # Daily flat rates for 1, 2, and 3 days

    total_fee = 0
    hours_processed = 0

    # Apply daily flat rates if the parking duration is more than 24 hours
    for days, rate in daily_rates:
        if duration_hours >= 24 * days:
            total_fee += rate
            duration_hours -= 24 * days
            hours_processed += 24 * days

    # Process remaining hours after applying daily rates
    while duration_hours > 0:
        applicable_rate_found = False
        for duration, rate, interval in rates:
            if duration is None or duration_hours < duration:
                # Calculate the charge for the remaining time if it doesn't fit exactly into a specific interval
                chargeable_duration = min(duration_hours, interval if duration is None else duration)
                total_fee += chargeable_duration / interval * rate
                duration_hours -= chargeable_duration
                applicable_rate_found = True
                break
            elif duration_hours >= duration:
                # Calculate the charge for the full rate duration
                total_fee += rate
                duration_hours -= duration

        if not applicable_rate_found:
            # If no applicable rate is found, charge for the last specified rate
            total_fee += duration_hours / interval * rate
            break

    return f"Total parking fee at Bahnhof: {total_fee:.2f} CHF"

def calculate_fee_bruehltor(arrival_datetime, duration_hours):
    # Defining rate details for Brühltor
    rates = {
        "day": [(1, 2.00), (None, 1.00, 0.5)],  # After 1st hour, charge per 30 minutes
        "night": [(1, 1.20), (None, 0.60, 0.5)]  # Night rates
    }
    daily_rate = 25  # Daily flat rate
    valid_hours = {"day": (7, 24), "night": (0, 7)}  # Operating hours

    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    total_fee = 0
    hours_left = duration_hours

    # Apply daily flat rate if applicable
    if hours_left >= 24:
        days = int(hours_left // 24)
        total_fee += days * daily_rate
        hours_left -= days * 24

    # Process hourly rates based on current time
    while hours_left > 0:
        if valid_hours["day"][0] <= current_time < valid_hours["day"][1]:
            # Apply daytime rates
            for (hours, rate, interval) in rates["day"]:
                if hours is None or hours_left <= hours:
                    hours_to_charge = min(hours_left, interval)
                    total_fee += hours_to_charge * rate
                    hours_left -= hours_to_charge
                    current_time += hours_to_charge
                    break
        else:
            # Apply nighttime rates
            for (hours, rate, interval) in rates["night"]:
                if hours is None or hours_left <= hours:
                    hours_to_charge = min(hours_left, interval)
                    total_fee += hours_to_charge * rate
                    hours_left -= hours_to_charge
                    current_time += hours_to_charge
                    break

        current_time = (current_time % 24)  # Reset time after midnight

    return f"Total parking fee at Brühltor: {total_fee:.2f} CHF"

def calculate_fee_burggraben(arrival_datetime, duration_hours):
    # Rates and times definitions
    standard_rates = {
        "day": [(1, 2.00), (None, 1.00, 0.5)],  # Day rates from 7 AM to midnight
        "night": [(1, 1.20), (None, 0.60, 0.5)]  # Night rates from midnight to 7 AM
    }
    weekend_rates = [(1, 2.40), (None, 1.20, 0.5)]  # Special weekend rates
    valid_hours = {"day": (7, 24), "night": (0, 7)}
    daily_rates = [(24, 25), (48, 50), (72, 75)]  # Flat rates for up to 3 days

    current_time = arrival_datetime.hour + arrival_datetime.minute / 60
    total_fee = 0
    hours_left = duration_hours

    # Check if it's a weekend day for special rates
    is_weekend = arrival_datetime.weekday() >= 5  # 5 for Saturday, 6 for Sunday

    # Apply daily flat rates if parking duration is long enough
    for duration, rate in daily_rates:
        if hours_left >= duration:
            total_fee += rate
            hours_left -= duration

    # Calculate hourly rates based on remaining hours
    while hours_left > 0:
        if valid_hours["day"][0] <= current_time < valid_hours["day"][1]:
            # Daytime rates
            rate_details = weekend_rates if is_weekend else standard_rates["day"]
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




