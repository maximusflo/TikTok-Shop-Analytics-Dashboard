# TikTok Shop Creator Performance Tracker
A data analytics dashboard built for TikTok Shop creators to track daily performance metrics, identify monetization trends, and evaluate efficiency of content over time.

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
- Visualizations

## Metrics Tracked
- Commission
- Gross Merchandise Value (GMV)
- Items Sold
- Videos
- Views
- Conversion Rate
- Average Commission Rate

## Installation
```bash
git clone https://github.com/yourusername/tiktok-shop-tracker.git
cd tiktok-shop-tracker
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
- Revenue Per 1,000 Views (RMP) metric
- Video logging
- Correlation visualizations
- Goal tracking



## Author 
Max Floren  
University of St. Thomas  
Computer Science