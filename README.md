# TikTok Shop Analytics Dashboard
A data analytics dashboard built for TikTok Shop creators to track daily performance metrics and evaluate efficiency of content over time.

Built with Python, Streamlit, SQLite, Pandas, and Plotly.

## Features
- Daily performance logging
- Editable past entries
- Persistent SQLite database storage
- Interactive analytics dashboard
- Date range filtering
- Metric calculations
- Commission rate analysis
- Conversion rate analysis
- RPM analysis
- Visualizations

## Metrics Tracked
- Commission
- Gross Merchandise Value (GMV)
- Items Sold
- Videos
- Views
- Conversion Rate
- Average Commission Rate
- Revenue per Thousand Views (RPM)

## Installation
```bash
git clone https://github.com/maximusflo/TikTok-Shop-Analytics-Dashboard.git
cd TikTok-Shop-Analytics-Dashboard
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage
Run the application:

```bash
streamlit run app.py
```

## Database Structure
|Column|Type|
|---|---|
|date|TEXT|
|commission|REAL|
|gmv|REAL|
|items_sold|INTEGER|
|videos|INTEGER|
|views|INTEGER|

## Future Improvements
- Performance grading/rank system
- User authentication
- Revenue forecasting
- Video logging
- Correlation visualizations
- Goal tracking
- Product click metric
- Attributed GMV metric
- Commission base metric

## Author 
Max Floren  
University of St. Thomas  
Computer Science