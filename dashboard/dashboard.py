import calendar
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pandas import DataFrame

# Helper function yang digunakan untuk mengubah rentang jam menjadi teks
def check_time_of_day(time):
    if time == 0:
        return "midnight"
    elif 0 < time < 4:
        return "late night"
    elif 4 <= time < 12:
        return "morning"
    elif 12 <= time < 13:
        return "noon"
    elif 13 <= time < 18:
        return "afternoon"
    elif 18 <= time < 20:
        return "evening"
    elif time >= 20:
        return "night"
    else:
        return ""

# Helper function yang digunakan untuk menyiapkan dataframe
def create_trend_bike_rental_df(df: DataFrame):
    bike_trend_df = df.groupby(by=["yr", "mnth"])["cnt"].sum().reset_index()
    bike_trend_df["yr"] = bike_trend_df["yr"].apply(lambda x: 2011 if x == 0 else 2012)
    bike_trend_df["mnth"] = bike_trend_df["mnth"].apply(lambda x: calendar.month_abbr[x])

    bike_trend_df["year_month"] = bike_trend_df["mnth"].astype(str) + "/" + bike_trend_df["yr"].astype(str)
    bike_trend_df.drop(columns=["yr", "mnth"], inplace=True)

    return bike_trend_df


def create_bike_renters_by_day_category_df(df: DataFrame):
    day_category = {
        "day": ["holiday", "workingday", "weekend"]
    }

    bike_rental_total_df = pd.DataFrame(data=day_category)

    rental_total = df["cnt"].sum()

    workingday_total_grouped = df.groupby(by="workingday")["cnt"].sum()
    holiday_total_grouped = df.groupby(by="holiday")["cnt"].sum()

    workingday_total = workingday_total_grouped.get(1, 0)
    holiday_total = holiday_total_grouped.get(1, 0)

    weekend_total = rental_total - (workingday_total + holiday_total)

    bike_rental_total_df["total"] = [holiday_total, workingday_total, weekend_total]

    return bike_rental_total_df


def create_bike_renters_by_weather_df(df: DataFrame):
    weathers = ["sunny", "mist/cloudy", "light rain/snow", "extreme weather"]

    rental_total_by_weather_df = df.groupby(by="weathersit")["cnt"].sum().reset_index()
    rental_total_by_weather_df["weathersit"] = rental_total_by_weather_df["weathersit"].apply(lambda x: weathers[x - 1])

    return rental_total_by_weather_df

def create_bike_renters_by_season_df(df: DataFrame):
    seasons = ["spring", "summer", "fall", "winter"]

    rental_total_by_season_df = df.groupby(by="season")["cnt"].sum().reset_index()
    rental_total_by_season_df["season"] = rental_total_by_season_df["season"].apply(lambda x: seasons[x - 1])

    return rental_total_by_season_df

def create_bike_renters_by_user(df: DataFrame):
    casual_total = df["casual"].sum()
    registered_total = df["registered"].sum()

    user_total = {
        "casual": casual_total,
        "registered": registered_total
    }

    return user_total

def create_bike_renters_by_time_df(df: DataFrame):
    df["time_of_day"] = df["hr"].apply(check_time_of_day)

    rental_total_by_time = df.groupby(by="time_of_day")["cnt"].sum().reset_index()

    return rental_total_by_time

# Load dataset
bike_rental_by_day_df = pd.read_csv("data/day.csv")
bike_rental_by_hour_df = pd.read_csv("data/hour.csv")

# Melakukan reset index
bike_rental_by_day_df.sort_values(by="dteday", inplace=True)
bike_rental_by_day_df.reset_index(inplace=True)

bike_rental_by_hour_df.sort_values(by="dteday", inplace=True)
bike_rental_by_hour_df.reset_index(inplace=True)

# Melakukan konversi tipe data kolom dteday menjadi datetime
bike_rental_by_day_df["dteday"] = pd.to_datetime(bike_rental_by_day_df["dteday"])
bike_rental_by_hour_df["dteday"] = pd.to_datetime(bike_rental_by_hour_df["dteday"])

# Filter data berdasarkan tanggal
min_date = bike_rental_by_day_df["dteday"].min()
max_date = bike_rental_by_day_df["dteday"].max()

# Membuat sidebar
with st.sidebar:

    # Menambahkan logo
    st.image("https://cdn-icons-png.flaticon.com/256/14645/14645344.png")

    # Mengambil tanggal awal dan tanggal akhir dari date_input
    start_date, end_date = st.date_input(
        label="Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Inisialiasi rentang tanggal pada dataframe
bike_rental_by_day_df = bike_rental_by_day_df[(bike_rental_by_day_df["dteday"] >= str(start_date)) & (bike_rental_by_day_df["dteday"] <= str(end_date))]
bike_rental_by_hour_df = bike_rental_by_hour_df[(bike_rental_by_hour_df["dteday"] >= str(start_date)) & (bike_rental_by_hour_df["dteday"] <=  str(end_date))]

# Menyiapkan dataframe
trend_bike_rental_df = create_trend_bike_rental_df(bike_rental_by_day_df)
bike_rental_by_day_category_df = create_bike_renters_by_day_category_df(bike_rental_by_day_df)
bike_rental_by_weather_df = create_bike_renters_by_weather_df(bike_rental_by_hour_df)
bike_rental_by_time_df = create_bike_renters_by_time_df(bike_rental_by_hour_df)
bike_rental_by_user = create_bike_renters_by_user(bike_rental_by_day_df)

# Menambahkan teks header
st.header("Bike Sharing Dashboard :sparkles:")

# Membuat tiga kolom
col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = bike_rental_by_day_df["cnt"].sum()
    st.metric("Total rentals", value=total_rentals)

with col2:
    total_registered_users = bike_rental_by_day_df["registered"].sum()
    st.metric("Total registered users", value=total_registered_users)

with col3:
    total_casual_users = bike_rental_by_day_df["casual"].sum()
    st.metric("Total casual users", value=total_casual_users)

# Membuat visualisasi tren peminjam sepeda dari tahun 2011 - 2012
st.subheader("Bike Rental Trends from 2011 to 2012")

fig, ax = plt.subplots(figsize=(20, 10))
ax.plot(
    trend_bike_rental_df["year_month"],
    trend_bike_rental_df["cnt"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="y", labelsize=25)
ax.tick_params(axis="x", labelsize=20, rotation=45)

st.pyplot(fig)

# Membuat visualisasi jumlah peminjam sepeda berdasakran kategori hari
st.subheader("Number of Bike Renters by Day Category")
fig, ax = plt.subplots(figsize=(16, 8))

colors = ["#D3D3D3", "#72BCD4", "#D3D3D3"]

sns.barplot(
    y="total",
    x="day",
    data=bike_rental_by_day_category_df,
    palette=colors,
    ax=ax
)

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="x", labelsize=20)
ax.tick_params(axis="y", labelsize=25)

st.pyplot(fig)

# Membuat visualisasi jumlah peminjam sepeda berdasarkan cuaca
st.subheader("Number of Bike Renters by Weather")
fig, ax = plt.subplots(figsize=(16, 8))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="cnt",
    y="weathersit",
    data=bike_rental_by_weather_df,
    palette=colors,
    ax=ax
)

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="x", labelsize=15)
ax.tick_params(axis="y", labelsize=20)

st.pyplot(fig)

# Membuat visualisasi jumlah peminjam sepeda berdasarkan jenis pengguna
st.subheader("Number of Bike Renters by User Type")
fig, ax = plt.subplots(figsize=(10, 5))

ax.pie(
    x=[bike_rental_by_user["casual"], bike_rental_by_user["registered"]],
    labels=("casual", "registered"),
    autopct="%1.1f%%",
    explode=(0, 0.1)
)

st.pyplot(fig)

# Membuat visualisasi jumlah peminjam sepeda berdasarkan waktu
st.subheader("Number of Bike Renters by Time")
fig, ax = plt.subplots(figsize=(16, 8))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="cnt",
    y="time_of_day",
    data=bike_rental_by_time_df,
    palette=colors,
    ax=ax
)

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="x", labelsize=15)
ax.tick_params(axis="y", labelsize=20)

st.pyplot(fig)

# Membuat visualisasi korelasi antar fitur
st.subheader("Correlation Bike Renters Count with Temperature, ATemperature, Humidity, and Windspeed")
fig, ax = plt.subplots(figsize=(10, 5))

selected_columns = ["temp", "atemp", "hum", "windspeed", "cnt"]

sns.heatmap(
    data=bike_rental_by_hour_df[selected_columns].corr(),
    ax=ax
)

st.pyplot(fig)

# Membuat footer
st.caption("Copyright (c) Refanz 2025")