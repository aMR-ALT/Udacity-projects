import datetime
import pyinputplus
import time
import pandas as pd
import numpy as np
import pyinputplus as pyip
import calendar
import distutils

pd.set_option('display.max_columns', None)

CITY_DATA = {'chicago': 'chicago.csv',
             'new york city': 'new_york_city.csv',
             'washington': 'washington.csv'}
chi = pd.read_csv(CITY_DATA["chicago"])
nyc = pd.read_csv(CITY_DATA["new york city"])
wsh = pd.read_csv(CITY_DATA["washington"])

city_selection = {
    "Chicago": chi,
    "New York": nyc,
    "Washington": wsh
}

# Utilities to convert day and month to int
class DayMonthUtility:
    day = {day: index for index, day in enumerate(calendar.day_name) if day}
    month = {month: index for index, month in enumerate(calendar.month_name[0:7]) if month}


available_city = ["chicago", "new york", "washington"]

choices_list = ["Time", "End Time", "", "Gender",
                "Month", "Day", "User Type"]

flter_input = {}


def check_data(prompt, data_type):
    """
    a function to check the type of data, using pyinputplus lib
    the main purpose was to reduce the code in get_filters() and to allow for a more readable code

    prompt(str): the message to be shown for the user
    data_type(str): for checking various data types
    return: for every type, it returns a dict updated with the assigned value
    """
    if data_type in choices_list[0:2]:
        print("Please enter start time first then end time\n")
        start_time = pyip.inputTime("Enter the time in hh:mm form\n", blank=True)
        flter_input["Time"] = start_time
        if not int(start_time.hour) == 0:
            end_time = pyip.inputTime("Enter the time in hh:mm form\n", blank=True)
            flter_input["End Time"] = end_time

            if int(end_time.hour - start_time.hour) < 0:
                print("Please make sure that the start time is before end time\n")
                check_data("", data_type)

    elif data_type.title() == "Month":
        month = pyip.inputMonth("Enter the month", blank=True)
        if month not in DayMonthUtility.month:
            print("Please notice that you can choose from the first six months only")
            check_data(prompt="", data_type="Month")
        elif True:
            flter_input[data_type.title()] = DayMonthUtility.month[month]

    elif data_type.title() == "Day":
        day = pyip.inputDayOfWeek("Enter the day", blank=True)
        flter_input[data_type.title()] = day

    elif data_type.title() == "User Type":
        flter_input["User Type"] = pyip.inputChoice(["Subscriber", "Customer"], prompt="Subscriber or customer?\n")

    while data_type.title() == "Gender":
        if data_type == "Gender" and flter_input["City"] != "Washington":
            data = input(prompt)
            flter_input[data_type.title()] = data.capitalize()

            while data.capitalize() not in ["Male", "Female"]:
                if not len(data) == 0:
                    check_data("It's okay to define gender whatever you want\n"
                               "however gender here means biological sex as it defined in the data",
                               "Gender\n")
                    break
                else:
                    break
        else:
            print("Please note that gender selection is only available for nyc and chicago")
        break


def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.
    Modified: allows user to choose apply his own filters

    Returns:
        (dic): a dictionary that contains specified city, month, and day in addition to
        another filters - if they were chosen -.
    """

    filled_flter = flter_input.copy()

    print('Hello! Let\'s explore some US bikeshare data!')
    print("Would you like to see data for Chicago, Newyork or Washington?\n")

    question1 = input()
    city = question1.title()
    while question1.lower() not in available_city:
        print("Please enter a city from the list")
        question1 = input().title()
        flter_input["City"] = question1
        city = flter_input["City"]
    flter_input["City"] = city

    # ask user to choose how to filter data, either manually or by choosing a predefined filters
    print("You will enter the period of time that the data will be filtered upon\n")
    print("But before this, would you like to apply more advanced filters?\n"
          "1- No\n"
          "2- Yes")
    question2 = pyip.inputNum(min=1, max=2)

    # defining a loop to encapsulate the two choices
    while int(question2) in [1, 2]:

        # a value which will be retrieved later to decide the type of data analysis
        flter_input["Type"] = "Normal"

        # response1, which contains the specified month or day,
        # is defined even if user decided to implement her/his filters
        response1 = pyip.inputChoice(["month", "day", "both"],
                                     prompt="Please specify the month or day, or both if you want\n")

        if response1.lower() == "both":
            flter_input["Day"] = pyip.inputDayOfWeek("Enter day\n")
            check_data("", "Month")

        elif response1.lower() in ["day", "month"]:
            check_data("write the {}".format(response1), data_type=response1.title())

        # a modification to allow choosing own specified filters
        if question2 == 2:
            user_input = input(
                'How would you like to filter the data? \n'
                '-Time \n-End Time\n-User Type\n'
                '-Gender(Note: only available for chicago and nyc)\n'
                'You can get your data by typing finish, you can also skip choosing filter by entering space\n')

            while user_input != "finish":

                if user_input.title() in choices_list:
                    check_data("Please enter your filter".title(), user_input.title())
                    print(
                        "You are back to the filter menus, please remember that you can finish selecting by typing finish\n")
                else:
                    print("please choose from the list\n"
                          "if you finished choosing, please type finish\n")
                user_input = input()
            else:
                question2 = 1
                flter_input["Type"] = "Advanced"

        if question2 == 1:
            print("Filters are:\n")
            for k, v in flter_input.items():
                print(str(k) + " = " + str(v))
            question3 = pyip.inputYesNo("Continue (Y/N)\n")
            # Convert yes/no to True or False so it can be used in terminating the function
            question3 = distutils.util.strtobool(question3)

            if question3:
                break
            else:
                continue

    print('-' * 40)
    return flter_input, city


def load_data(city, fltr):
    """
    Loads data for the specified city and filters by month and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (dict) fltr - a dict which contains all the filters to be applied
    Returns:
        df - Pandas DataFrame containing city data filtered either normally or advanced
    """
    city = city
    df = city_selection[city]
    df_date = pd.to_datetime(df['Start Time'])
    month_filter = df_date.dt.month
    day_filter = df_date.dt.day_name()
    start_hour_filter = df_date.dt.time
    end_hour_filter = pd.to_datetime(df['End Time']).dt.time

    # Main filter process, it's applied for both advanced and normal types
    if "Day" not in flter_input.keys():
        df = df[month_filter == flter_input["Month"]]
    elif "Month" not in flter_input.keys():
        df = df[day_filter == str(flter_input["Day"]).capitalize()]
    else:
        df = df[day_filter == str(flter_input["Day"]).capitalize()]
        df = df[month_filter == flter_input["Month"]]

    # A non-pythonic way to filter data based on selected filters, the amount of time wasn't enough
    # to implement a more elegant code
    if flter_input["Type"] == "Advanced":
        try:
            df = df[df['Gender'] == flter_input["Gender"]]
        except KeyError:
            None
        try:
            df = df[(start_hour_filter >= flter_input["Time"])
                    & (end_hour_filter <= flter_input["End Time"])]
        except KeyError:
            None
        try:
            df = df[df['User Type'] == flter_input["User Type"]]
        except KeyError:
            None

    return df


def time_stats(df):
    """Displays statistics on the most frequent times of travel."""

    print('\nCalculating The Most Frequent Times of Travel...\n')

    df_date = pd.to_datetime(df["Start Time"])

    # I chose not to show the popular month as the data was in a somewhat limited range,
    # and it's seemed for me that it's meaningless to show the popular element in only six elements
    # also I've deleted the "this took.." part as it's made input more crowded without a real benefit

    # display the most common day of week
    if "Day" not in flter_input.keys():
        df_date["first"] = df_date.dt.day_name()
        popular_day = df_date["first"].mode()[0]
        print("popular day is {}".format(popular_day))

    # display the most common start hour
    df_date["second"] = pd.to_datetime(df["Start Time"]).dt.hour
    popular_hour = df_date['second'].mode()[0]
    print("popular hour is {}".format(popular_hour))
    print('-' * 40)


def station_stats(df):
    """Displays statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')

    # display most commonly used start station
    most_first_station = df["Start Station"].mode()[0]
    print("most commonly used start station: ", most_first_station)

    # display most commonly used end station
    most_end_station = df["End Station"].mode()[0]
    print("most commonly used end station: ", most_end_station)
    # display most frequent combination of start station and end station trip
    ready_data = df.loc[:, ["Start Station", "End Station"]]
    most_combination_station = ready_data["Start Station"] + ready_data["End Station"]
    indx = most_combination_station.value_counts()
    print("most frequent combination of start station and end station trip:\n", indx[indx == indx.max()].index[0])

    print('-' * 40)


def trip_duration_stats(df):
    """Displays statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')

    trip_duration = df["Trip Duration"].astype(int)

    # display total travel time
    print("total travel time: ", trip_duration.count())
    # display mean travel time
    print("mean travel time: ", int(trip_duration.mean()))

    print('-' * 40)


def user_stats(df):
    """Displays statistics on bikeshare users."""
    print('\nCalculating User Stats...\n')

    # Display counts of user types
    print(df["User Type"].value_counts().to_string())

    # check for city because washington doesn't contain birth year and gender data
    if flter_input["City"] != "Washington":
        user = df[["Gender", "Birth Year"]]
        # Display counts of gender
        print(user["Gender"].value_counts().to_string())

        # Display earliest, most recent, and most common year of birth
        birth_year = user["Birth Year"].dropna()  # .astype(int)
        earliest = birth_year.min()
        print("Earliest birth year: ", int(earliest))
        most_recent = birth_year.max()
        print("Most recent birth year: ", int(most_recent))
        most_common = birth_year.mode()
        print("most common birthday: ", int(most_common[0]))
    print('-' * 40)


def display_raw_data(df):
    """
    Takes dataframe and gives user the choice to display raw data if he/she wants
    """
    ask_user = pyip.inputYesNo("Would you like to show the raw data for the city you've selected?")

    # I used index to show five after five instead of random sample
    if ask_user.lower() == "yes":
        n = 5
        print(df.head(n).fillna("None"))
        print("Would you like to see more data?(another 5 rows will be shown)")
        ask_repeat = pyinputplus.inputYesNo("y/n")
        while ask_repeat.lower() == "yes":
            n += 5
            try:
                print(df.fillna("None").iloc[n:n + 5])
                ask_repeat = pyinputplus.inputYesNo(
                    prompt="Would you like to see more data?(another 5 rows will be shown)")
            except IndexError: print("There is no more data to show!")


def main():
    while True:
        filled_flter_input, city = get_filters()
        df = load_data(city, flter_input)

        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)
        display_raw_data(df)

        restart = input('\nWould you like to restart? Enter yes or no.\n')
        if restart.lower() != 'yes':
            break


if __name__ == "__main__":
    main()

"""
    I'm sorry, i know that my code isn't the best, it isn't also elegant, and not even well documented
    but my time was highly limited, I wrote this in only 3 days but sitting 10 hours everyday, i wanted to make it more
    user friendly and even add a GUI, but even the functionally of advanced filter isn't complete. I wished if i had more
    time to make a better program. Again, i repeat my apologizes, it will be understandable if there were alot of
    notes or - sitting my expectations for reality - if there was a problem anywhere, This doesn't mean by anyways
    that i'm flattering or playing weak to be passed, it's just an admission that my work wasn't that good.
    Thanks for your time.
    """