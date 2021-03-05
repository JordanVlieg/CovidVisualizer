# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import matplotlib.pyplot as plt
from collections import deque
from matplotlib.ticker import MaxNLocator
import json

CDC_API = "https://data.cdc.gov/resource/9mfq-cb36.json"
LIMIT = 1000


def rolling_avg(data, days):
    averages = []
    rolling_sum = 0
    for i in range(len(data)):
        rolling_sum += data[i]
        if i >= days:
            rolling_sum -= data[i - days]
        averages.append(rolling_sum/days)
    return averages


def choose_n_elems(data, n):
    vals = []
    for i in range(len(data)):
        if i % n == 0:
            vals.append(data[i])
    return vals


def call_cdc_api():
    params = {"$limit": LIMIT, "$offset": 0, "$order": "submission_date"}
    i = 0
    compound_data = {}
    fields = ["submission_date", "tot_cases", "new_case", "tot_death", "new_death"]
    usa_data = {}
    while True:
        params["$offset"] = i * LIMIT
        i += 1
        data = requests.get(CDC_API, params)
        print(i)
        json_data = data.json()
        if data.status_code is not 200 or len(json_data) is 0:
            break

        for row in json_data:
            state = row["state"]
            if state not in compound_data:
                compound_data[state] = {}
            for field in fields:
                if field not in compound_data[state]:
                    compound_data[state][field] = []
                if field is "submission_date":
                    compound_data[state][field].append(row[field])
                    if row["submission_date"] not in usa_data:
                        usa_data[row["submission_date"]] = {}
                else:
                    compound_data[state][field].append(float(row[field]))
                    if field not in usa_data[row["submission_date"]]:
                        usa_data[row["submission_date"]][field] = 0.0
                    usa_data[row["submission_date"]][field] += float(row[field])

    with open('usa_cdc_data.json', 'w') as fp:
        json.dump(usa_data, fp)
    with open('state_cdc_data.json', 'w') as fp:
        json.dump(compound_data, fp)


def process_usa_data(field, sparse):
    with open('usa_cdc_data.json', 'r') as fp:
        usa_data = json.load(fp)

    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(MaxNLocator(20))
    ax.yaxis.set_major_locator(MaxNLocator(10))
    dates = list(usa_data.keys())
    if sparse:
        dates = choose_n_elems(dates, 7)
    simple_dates = list(map(lambda x: x[2:10], dates))
    ax.set(xlabel='Date', ylabel=field)
    ax.set_title('USA')
    new_cases = list(map(lambda x: x[field], usa_data.values()))
    avg_cases = rolling_avg(new_cases, 7)
    if sparse:
        avg_cases = choose_n_elems(avg_cases, 7)
    ax.bar(simple_dates, avg_cases)
    ax.grid()
    plt.show()


def process_state_data(state, field, sparse, leftbound):
    with open('state_cdc_data.json', 'r') as fp:
        compound_data = json.load(fp)

    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(MaxNLocator(20))
    ax.yaxis.set_major_locator(MaxNLocator(10))
    dates = compound_data[state]["submission_date"]
    if sparse:
        dates = choose_n_elems(dates, 7)
    simple_dates = list(map(lambda x: x[2:10], dates))
    ax.set(xlabel='Date', ylabel=field)
    ax.set_title(state)
    avg_cases = rolling_avg(compound_data[state][field], 7)
    #avg_cases = compound_data[state][field]
    if sparse:
        avg_cases = choose_n_elems(avg_cases, 7)
    if leftbound is not None:
        simple_dates = simple_dates[leftbound:]
        avg_cases = avg_cases[leftbound:]
    ax.bar(simple_dates, avg_cases)
    #ax.bar(simple_dates, compound_data[state][field][leftbound:])
    ax.grid()
    plt.show()


if __name__ == '__main__':
    #call_cdc_api()
    process_state_data("CA", "new_case", False, 250)
    #process_usa_data("new_case", False)
    #test_plot()
