# 🌍 Global Time Zone Dashboard

## 📖 About

The Global Time Zone Dashboard is a Streamlit based web application that displays the current local time across different regions worldwide. I created this tool to easily compare time zones, especially after Mexico’s CST time zone stopped observing daylight saving time.

## 🌟 Features

- Accurate local time display accounting for daylight saving time and regional time policies
- Interactive world map showing selected locations and their current time
- Ability to add custom locations using country, state, and city information
- For now, uses a json to storage added locations - I'll improve it in a future

## 🚀 Installation

1. Clone this repository:

   ```
   git clone https://github.com/Hckmar9/timeyo
   cd timeyo
   ```

2. Install the required dependencies:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## 💻 Usage

1. Run the Streamlit app:

   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Use the sidebar to select locations and customize the dashboard.

4. Add custom locations using the "Add Custom Location" expander in the sidebar.

## 🛠️ Dependencies

- streamlit
- pandas
- pytz
- plotly
- folium
- streamlit-folium
- geopy
- timezonefinder

## 🤝 Contributing

Contributions are always welcome! Please feel free to submit a pull request.

## 📄 License

This project is open source and available under the MIT License

---

Made Nerdily ❤️ by Hckmar9
