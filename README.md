# TikTok Shop Analytics Dashboard
A full-stack data analytics dashboard built for TikTok Shop creators to track daily performance metrics over time.

Built with Python, Streamlit, PostgreSQL, Supabase, Pandas, and Plotly.

**[Live Demo](https://tiktok-shop-analytics-dashboard.streamlit.app/)**

## Features
- Google user authentication
- Daily performance logging
- Editable past entries
- Persistent PostgreSQL database storage
- Interactive analytics dashboard
- Date range filtering
- Metric calculations
- Commission rate analysis
- Conversion rate analysis
- RPM analysis
- Monthly goal setting and tracking
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


## Database Structure
`daily_stats`
|Column|Type|
|---|---|
|user_id|TEXT|
|date|DATE|
|commission|REAL|
|gmv|REAL|
|items_sold|INTEGER|
|videos|INTEGER|
|views|INTEGER|

---  

`monthly_goals`
|Column|Type|
|---|---|
|user_id|TEXT|
|month|DATE|
|analytic|TEXT|
|goal|NUMERIC|

## Tech Stack
- **Python** — application logic and data processing
- **Streamlit** — web application and dashboard
- **PostgreSQL** — persistent relational database
- **Supabase** — hosted PostgreSQL database
- **Pandas** — data manipulation and analysis
- **Plotly** — interactive data visualization
- **Google OAuth** — user authentication

## Future Improvements
- Performance grading/rank system
- Revenue forecasting
- Video logging
- Correlation visualizations
- Product click metric
- Attributed GMV metric
- Commission base metric
- Row Level Security
- Demo mode

## Author 
**Max Floren**  
University of St. Thomas  
Computer Science