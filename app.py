import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import metrics
import utils
import database
from sqlalchemy import text
from zoneinfo import ZoneInfo

st.set_page_config(layout='wide')

today = datetime.datetime.now(ZoneInfo("America/Chicago")).date()

# Remove increment and decrement buttons from data input
st.markdown("""
<style>
button[aria-label="Decrement"] {
    display: none;
}

button[aria-label="Increment"] {
    display: none;
}

button {
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# user authentication
if not st.user.is_logged_in:
    st.title('TikTok Shop Creator Performance Dashboard')
    st.write('#### Track your TikTok Shop performance data.')
    st.divider()
    st.button(
            'Sign in with Google',
            on_click=st.login,
        )

    st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 20px;
        left: 0;
        width: 100%;
        text-align: center;
        color: gray;
        font-size: 14px;
    }
    </style>

    <div class="footer">
        Built with Python · Streamlit · PostgreSQL · Pandas · Plotly
    </div>
    """, unsafe_allow_html=True)

    st.stop()

user_id = st.user.email

# initialize database
connection = database.get_connection()

st.title("TikTok Shop Creator Performance Tracker")

# side bar
st.sidebar.write(f'Logged in as {st.user.name}')
st.sidebar.write(f'Email: {st.user.email}')
st.sidebar.button('Log out', on_click=st.logout)

tab1, tab2, tab3 = st.tabs(['Analytics', 'Daily Log', 'Data'])

df = utils.load_data(connection, user_id)

# Analytics tab
with tab1:
    one, two, three, four, five = st.columns([1.6, 2.1, 1.7, 1.9, 19])

    # filter dates button
    single_day = False
    with five:
        with st.popover('Filter Dates'):
            df['date'] = pd.to_datetime(df['date']).dt.date
        
            if not df.empty:
                min_date = df['date'].min()
                max_date = df['date'].max()
                date_range = st.date_input('Date Range', value=(min_date, max_date))
            else:
                today = datetime.datetime.now(ZoneInfo("America/Chicago")).date()
                date_range = st.date_input('Date Range', value=(today, today))
        
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date = date_range[0]
                end_date = date_range[1]
            else:
                start_date = date_range[0]
                end_date = date_range[0]

    # today button
    with one:
        if st.button('Today', use_container_width=True):
            date_range = (today, today)
            start_date = date_range[0]
            end_date = date_range[0]

    # yesterday button
    with two:
        if st.button('Yesterday', use_container_width=True):
            yesterday = today - datetime.timedelta(days=1)
            date_range = (yesterday, yesterday)
            start_date = date_range[0]
            end_date = date_range[0]

    # 7 days button
    with three:
        if st.button('7 Days', use_container_width=True):
            week_ago = today - datetime.timedelta(days=6)
            date_range = (week_ago, today)
            start_date = date_range[0]
            end_date = date_range[1]

    # 30 days button
    with four:
        if st.button('30 Days', use_container_width=True):
            month_ago = today - datetime.timedelta(days=29)
            date_range = (month_ago, today)
            start_date = date_range[0]
            end_date = date_range[1]

    if start_date == end_date:
        single_day = True
        st.write(f"**{start_date.strftime('%b %d, %Y').replace(' 0', ' ')}** (CDT)")
    else:
        st.write(f"**{start_date.strftime('%b %d, %Y').replace(' 0', ' ')} - {end_date.strftime('%b %d, %Y').replace(' 0', ' ')}** (CDT)")

    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)] if not df.empty else pd.DataFrame(columns=df.columns)
    
    col1, col2, col3, col4, col5 = st.columns(5)

    # get max rows if available
    if filtered_df.empty:
        st.warning('No data available.')
    else:
        max_commission_row = utils.get_max_row(filtered_df, 'commission')
        max_gmv_row = utils.get_max_row(filtered_df, 'gmv')
        max_items_row = utils.get_max_row(filtered_df, 'items_sold')
        max_videos_row = utils.get_max_row(filtered_df, 'videos')
        max_views_row = utils.get_max_row(filtered_df, 'views')

    # performance metrics
    with col1:  # commission
        if filtered_df.empty:
            st.metric('Total Commission', '$0')
            if not single_day:
                st.metric('Avg. Daily Commission', '$0')
            #st.metric('Highest Commission Day', '-')
        else:
            st.metric('Total Commission', f"${filtered_df['commission'].sum():,.2f}")
            if not single_day:
                st.metric('Avg. Daily Commission', f"${filtered_df['commission'].mean():,.2f}")
            #st.metric('Highest Commission Day', f"${max_commission_row['commission']:,.2f}")

    with col2:  # GMV
        if filtered_df.empty:
            st.metric('Total GMV', '$0')
            if not single_day:
                st.metric('Avg. Daily GMV', '$0')
            #st.metric('Highest GMV Day', '-')
        else:
            st.metric('Total GMV', f"${filtered_df['gmv'].sum():,.2f}")
            if not single_day:
                st.metric('Avg. Daily GMV', f"${filtered_df['gmv'].mean():,.2f}")
            #st.metric('Highest GMV Day', f"${max_gmv_row['gmv']:,.2f}")

    with col3:  # items sold
        if filtered_df.empty:
            st.metric('Total Items Sold', '0')
            if not single_day:
                st.metric('Avg. Daily Items Sold', '0')
            #st.metric('Highest Item Sales Day', '-')
        else:
            st.metric('Total Items Sold', f"{int(filtered_df['items_sold'].sum()):,}")
            if not single_day:
                st.metric('Avg. Daily Items Sold', f"{float(filtered_df['items_sold'].mean()):,.1f}")
            #st.metric('Highest Item Sales Day', f"{max_items_row['items_sold']:,}")

    with col4:
        if filtered_df.empty:
            st.metric('Total Videos Posted', '0')
            if not single_day:
                st.metric('Avg. Daily Videos Posted', '0')
        else:
            st.metric('Total Videos Posted', f"{int(filtered_df['videos'].sum()):,}")
            if not single_day:
                st.metric('Avg. Daily Videos Posted', f"{float(filtered_df['videos'].mean()):,.1f}")
    
    with col5:  # views
        if filtered_df.empty:
            st.metric('Total Views', '0')
            if not single_day:
                st.metric('Avg. Daily Views', '0')
            #st.metric('Highest View Day', '-')
        else:
            st.metric('Total Views', f"{filtered_df['views'].sum():,}")
            if not single_day:
                st.metric('Avg. Daily Views', f"{int(filtered_df['views'].mean()):,}")
            #st.metric('Highest View Day', f"{max_views_row['views']:,}")

    c1, c2, c3 = st.columns(3)

    # display average commission rate and quality
    with c1:
        if filtered_df.empty or filtered_df['gmv'].sum() == 0:
            st.metric('Average Commission Rate', '-')
        else:
            avg_c_rate = metrics.avg_commission_rate(filtered_df)
            if avg_c_rate >= 20:
                quality = 'Excellent'
            elif avg_c_rate >= 15:
                quality = 'Great'
            elif avg_c_rate >= 10:
                quality = 'Good'
            elif avg_c_rate >= 5:
                quality = 'Weak'
            else:
                quality = 'Poor'
            
            st.metric('Average Commission Rate', f"{avg_c_rate}% - {quality}")

    # display conversion rate and quality
    with c2:
        if filtered_df.empty or filtered_df['views'].sum() == 0:
            st.metric('Conversion Rate', '-')
        else: 
            conv_rate = metrics.conversion_rate(filtered_df)
            if conv_rate >= 0.20:
                quality = 'Excellent'
            elif conv_rate >= 0.10:
                quality = 'Great'
            elif conv_rate >= 0.05:
                quality = 'Good'
            elif conv_rate >= 0.01:
                quality = 'Weak'
            else:
                quality = 'Poor'

            st.metric('Conversion Rate', f"{conv_rate}% - {quality}")

    # display RPM and quality
    with c3:
        if filtered_df.empty or filtered_df['views'].sum() == 0:
            st.metric('RPM', '-')
        else:
            rpm = metrics.rpm(filtered_df)
            if rpm >= 10:
                quality = 'Excellent'
            elif rpm >= 5:
                quality = 'Great'
            elif rpm >= 1.5:
                quality = 'Good'
            elif rpm >= 1:
                quality = 'Weak'
            else:
                quality = 'Poor'

            st.metric('RPM', f'${rpm} - {quality}')

    # commission line chart
    commission_fig = px.line(filtered_df, x='date', y='commission', title='Daily Commission')
    commission_fig.update_traces(line=dict(color='springgreen'))
    commission_fig.update_layout(yaxis=(dict(tickprefix='$')))
    st.plotly_chart(commission_fig, width='stretch')
    
    # views line chart
    views_fig = px.line(filtered_df, x='date', y='views', title='Daily Views')
    views_fig.update_traces(line=dict(color='royalblue'))
    st.plotly_chart(views_fig, width='stretch')

    # GMV line chart
    #    gmv_fig = px.line(filtered_df, x='date', y='gmv', title='Daily GMV')
    #    gmv_fig.update_traces(line=dict(color='green'))
    #    gmv_fig.update_layout(yaxis=(dict(tickprefix='$')))
    #    st.plotly_chart(gmv_fig, width='stretch')

    # videos posted line chart
    #    items_fig = px.line(filtered_df, x='date', y='videos', title='Daily Videos Posted')
    #    items_fig.update_traces(line=dict(color='orange'))
    #    st.plotly_chart(items_fig, width='stretch')

# Daily Log tab
with tab2:
    left, right = st.columns([1.75, 1])

    # data input
    with left:
        col1, col2, col3, col4, col5, col6 = st.columns([1.3, 1.4, 1, 1.1, 1.2, 1])

        with col1:  # date
            current_date = st.date_input('Date', value=today)
            st.write(f"Date: {current_date.strftime('%b %d, %Y').replace(' 0', ' ')}")

        with col2:  # commission
            commission = utils.float_input('commission', 'Commission', df, current_date)

        with col3:  # gmv
            gmv = utils.float_input('gmv', 'GMV', df, current_date)

        with col4:  # items_sold
            items_sold = utils.integer_input('items_sold', 'Items Sold', df, current_date)

        with col5: # videos posted
            videos = utils.integer_input('videos', 'Videos Posted', df, current_date)

        with col6:  # views
            views = utils.integer_input('views', 'Views', df, current_date)

        button_label = 'Save'

    # warns user they are updating an existing entry date
    warning_box = st.empty()
    if utils.date_exists(df, current_date):
        warning_box.info(f'About to update existing entry for {current_date}')
        button_label = 'Update'

    if st.button(button_label):

        # adding a new entry to data
        if str(current_date) not in df['date'].astype(str).values:

            with connection.session as session:
                session.execute(
                    text('''
                        INSERT INTO daily_stats
                        (user_id, date, commission, gmv, items_sold, videos, views)
                        VALUES (:user_id, :date, :commission, :gmv, :items_sold, :videos, :views)
                    '''),
                    {
                        'user_id': user_id,
                        'date': str(current_date),
                        'commission': commission,
                        'gmv': gmv,
                        'items_sold': items_sold,
                        'videos': videos,
                        'views': views
                    }
                )
                
                session.commit()

            df = utils.load_data(connection, user_id)
            st.success(f'Saved entry for {current_date}.')

        # updating existing entry
        else:
            with connection.session as session:
                session.execute(
                    text('''
                        UPDATE daily_stats
                        SET
                            commission = :commission,
                            gmv = :gmv,
                            items_sold = :items_sold,
                            videos = :videos,
                            views = :views
                        WHERE user_id = :user_id AND date = :date
                    '''),
                    {
                        'commission': commission,
                        'gmv': gmv,
                        'items_sold': items_sold,
                        'videos': videos,
                        'views': views,
                        'user_id': user_id,
                        'date': str(current_date)
                    }
                )
                session.commit()

            df = utils.load_data(connection, user_id)
            warning_box.empty()
            st.success(f'Updated entry for {current_date}')

# Data tab
with tab3:
    st.title('All Data')

    left1, right1 = st.columns(2)
    
    # data table
    with left1:
        st.dataframe(
            df.style.format({
                'gmv' : '${:,.2f}',
                'commission' : '${:,.2f}',
                'items_sold' : '{:,}',
                'views' : '{:,}'
                }),
                hide_index=True,
                width='stretch'
        )