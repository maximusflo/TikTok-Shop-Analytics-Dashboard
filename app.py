import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
import datetime
import metrics
import utils
import database

connection = database.get_conection()
cursor = connection.cursor()
database.initialize_database(connection)


st.set_page_config(layout='wide')

st.title('TikTok Shop Creator Performance Tracker')


tab1, tab2, tab3 = st.tabs(['Daily Log', 'Analytics', 'Data'])

df = utils.load_data(connection)

# Daily Log tab
with tab1:
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # data input
    with col1:  # date
        current_date = st.date_input('Date')
        st.write(f'Date: {str(current_date)}')

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
        data = {
            'date' : [current_date],
            'commission' : [commission],
            'gmv' : [gmv],
            'items_sold' : [items_sold],
            'videos' : [videos],
            'views' : [views]
        }
        new_df = pd.DataFrame(data)

        # adding a new entry to data
        if str(current_date) not in df['date'].astype(str).values:
            cursor.execute(
                '''
                INSERT INTO daily_stats
                (date, commission, gmv, items_sold, videos, views)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (
                    str(current_date),
                    commission,
                    gmv,
                    items_sold,
                    videos,
                    views
                )
            )
            connection.commit()
            df = utils.load_data(connection)
            st.success(f'Saved entry for {current_date}.')

        # updating existing entry
        else:
            cursor.execute(
                '''
                UPDATE daily_stats
                SET
                    commission = ?,
                    gmv = ?,
                    items_sold = ?,
                    videos = ?,
                    views = ?
                WHERE date = ?
                ''',
                (
                    commission,
                    gmv,
                    items_sold,
                    videos,
                    views,
                    str(current_date)
                )
            )
            connection.commit()
            df = utils.load_data(connection)
            warning_box.empty()
            st.success(f'Updated entry for {current_date}')

# Analytics tab
with tab2:
    one, two, three, four, five = st.columns(5)

    # filter dates
    with one:
        df['date'] = pd.to_datetime(df['date']).dt.date

        if not df.empty:
            min_date = df['date'].min()
            max_date = df['date'].max()
            date_range = st.date_input('Date Range', value=(min_date, max_date))
        else:
            today = datetime.date.today()
            date_range = st.date_input('Date Range', value=(today, today))

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date = date_range[0]
            end_date = date_range[1]
        else:
            start_date = date_range[0]
            end_date = date_range[0]

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
            st.metric('Avg. Daily Commission', '$0')
            #st.metric('Highest Commission Day', '-')
        else:
            st.metric('Total Commission', f"${filtered_df['commission'].sum():,.2f}")
            st.metric('Avg. Daily Commission', f"${filtered_df['commission'].mean():,.2f}")
            #st.metric('Highest Commission Day', f"${max_commission_row['commission']:,.2f}")

    with col2:  # GMV
        if filtered_df.empty:
            st.metric('Total GMV', '$0')
            st.metric('Avg. Daily GMV', '$0')
            #st.metric('Highest GMV Day', '-')
        else:
            st.metric('Total GMV', f"${filtered_df['gmv'].sum():,.2f}")
            st.metric('Avg. Daily GMV', f"${filtered_df['gmv'].mean():,.2f}")
            #st.metric('Highest GMV Day', f"${max_gmv_row['gmv']:,.2f}")

    with col3:  # items sold
        if filtered_df.empty:
            st.metric('Total Items Sold', '0')
            st.metric('Avg. Daily Items Sold', '0')
            #st.metric('Highest Item Sales Day', '-')
        else:
            st.metric('Total Items Sold', f"{int(filtered_df['items_sold'].sum()):,}")
            st.metric('Avg. Daily Items Sold', f"{float(filtered_df['items_sold'].mean()):,.1f}")
            #st.metric('Highest Item Sales Day', f"{max_items_row['items_sold']:,}")

    with col4:
        if filtered_df.empty:
            st.metric('Total Videos Posted', '0')
            st.metric('Avg. Daily Videos Posted', '0')
        else:
            st.metric('Total Videos Posted', f"{int(filtered_df['videos'].sum()):,}")
            st.metric('Avg. Daily Videos Posted', f"{float(filtered_df['videos'].mean()):,.1f}")
    
    with col5:  # views
        if filtered_df.empty:
            st.metric('Total Views', '0')
            st.metric('Avg. Daily Views', '0')
            #st.metric('Highest View Day', '-')
        else:
            st.metric('Total Views', f"{filtered_df['views'].sum():,}")
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
                quality = 'Good'
            elif avg_c_rate >= 10:
                quality = 'Standard'
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
            if conv_rate >= 0.2:
                quality = 'Elite'
            elif conv_rate >= 0.1:
                quality = 'Excellent'
            elif conv_rate >= 0.05:
                quality = 'Great'
            elif conv_rate >= 0.01:
                quality = 'Good'
            elif conv_rate >= 0.005:
                quality = 'Weak'
            else:
                quality = 'Poor'

            st.metric('Conversion Rate', f"{conv_rate}% - {quality}")

    left, right = st.columns(2)

    # commission line chart
    with left:
        commission_fig = px.line(filtered_df, x='date', y='commission', title='Daily Commission')
        commission_fig.update_traces(line=dict(color='springgreen'))
        commission_fig.update_layout(yaxis=(dict(tickprefix='$')))
        st.plotly_chart(commission_fig, width='stretch')
    
    # views line chart
    with right:
        views_fig = px.line(filtered_df, x='date', y='views', title='Daily Views')
        views_fig.update_traces(line=dict(color='royalblue'))
        st.plotly_chart(views_fig, width='stretch')

    # GMV line chart
    with left:
        gmv_fig = px.line(filtered_df, x='date', y='gmv', title='Daily GMV')
        gmv_fig.update_traces(line=dict(color='green'))
        gmv_fig.update_layout(yaxis=(dict(tickprefix='$')))
        st.plotly_chart(gmv_fig, width='stretch')

    with right: # videos posted line chart
        items_fig = px.line(filtered_df, x='date', y='videos', title='Daily Videos Posted')
        items_fig.update_traces(line=dict(color='orange'))
        st.plotly_chart(items_fig, width='stretch')

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

connection.close()