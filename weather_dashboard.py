import os
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_forecast(city: str):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    res = requests.get(url, params=params, timeout=20)
    return res.json()

def process_data(data: dict) -> pd.DataFrame:
    rows = []
    for entry in data.get("list", []):
        rows.append({
            "datetime": entry["dt_txt"],
            "temp": entry["main"]["temp"],
            "feels_like": entry["main"]["feels_like"],
            "humidity": entry["main"]["humidity"],
            "condition": entry["weather"][0]["description"].title(),
        })
    df = pd.DataFrame(rows)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = df["datetime"].dt.date
    return df

st.title("🌦 5-Day Weather Forecast")

city = st.text_input("Enter city name:", "karimnagar,IN")

if st.button("Get Forecast"):
    if not API_KEY:
        st.error("❌ API Key missing. Add it to your .env file as OPENWEATHER_API_KEY")
        st.stop()

    data = get_forecast(city)

    if str(data.get("cod")) != "200":
        st.error(f"API error: {data.get('message', 'Unknown error')}")
        st.stop()

    st.success(f"Forecast for {data['city']['name']}, {data['city']['country']}")

    # Process into dataframe
    df = process_data(data)

    # Show next 10 entries
    st.subheader("Next 10 forecast entries")
    for _, r in df.head(10).iterrows():
        st.text(f"{r['datetime']:%d %b %Y %H:%M} | 🌡 {r['temp']}°C | {r['condition']}")

    # Full forecast table
    st.subheader("Full Forecast Table")
    st.dataframe(df[["datetime", "temp", "feels_like", "humidity", "condition"]],
                 use_container_width=True)

    # ---------- Temperature Trend ----------
    st.subheader("Temperature Trend")
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(x="datetime", y="temp", data=df, marker="o", ax=ax, color="royalblue")
    ax.set_title("Temperature Over Time", fontsize=14)
    ax.set_xlabel("Date/Time")
    ax.set_ylabel("Temperature (°C)")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

    # ---------- Daily Average Temperature ----------
    st.subheader("Average Daily Temperature")
    daily = df.groupby("date")["temp"].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(x="date", y="temp", data=daily, ax=ax2, palette="coolwarm")
    ax2.set_title("Avg Temperature by Day", fontsize=14)
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Temperature (°C)")
    st.pyplot(fig2)