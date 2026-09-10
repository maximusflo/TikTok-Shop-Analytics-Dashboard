import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import metrics
import utils
import database
from sqlalchemy import text
from zoneinfo import ZoneInfo

st.set_page_config(page_title='Creator Analytics', page_icon='images/logo.png', layout='wide')

today = datetime.datetime.now(ZoneInfo('America/Chicago')).date()

DEMO_USER_ID = 'demo-user'

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
if not st.user.is_logged_in and not st.session_state.get('demo_mode', False):
    st.title('Creator Analytics', anchor=False, text_alignment='center')
    st.markdown('##### Track and analyze your affiliate performance data.', anchors=False, text_alignment='center')

    st.space()

    flex = st.container(horizontal=True, horizontal_alignment='center')

    if flex.button('Sign in with Google', icon=':material/login:'):
        st.login()
    if flex.button('Try Demo'):
        st.session_state.demo_mode = True
        st.rerun()

    st.space()

    st.image('images/screenshot.png', output_format='PNG')

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

    """, unsafe_allow_html=True)

    st.stop()

if st.session_state.get('demo_mode', False):
    user_id = DEMO_USER_ID
else:
    user_id = st.user.email

# initialize database
connection = database.get_connection()

# side bar
st.sidebar.title('Creator Analytics')
if not st.session_state.get('demo_mode', False):
    st.sidebar.write(f'Logged in as {st.user.name}')
    st.sidebar.write(f'Email: {st.user.email}')
    st.sidebar.space()
    st.sidebar.button('Log out', on_click=st.logout)
else:
    st.title('Creator Analytics - DEMO MODE', anchor=False)
    st.info('*All data shown is fictional and for demonstration purposes only.*', icon=':material/info_i:')

    st.sidebar.write(f'Logged in as demo user')
    st.sidebar.space()
    st.sidebar.button('Exit Demo', on_click=st.logout)

tab1, tab2, tab3, tab4 = st.tabs(['Analytics', 'Daily Log', 'Goals', 'Data'])

df = utils.load_data(connection, user_id)

### Analytics tab
with tab1:

    # filter dates button
    single_day = False

    df['date'] = pd.to_datetime(df['date']).dt.date

    start_date = df['date'].min()
    end_date = df['date'].max()

    @st.dialog('Select Date Range')
    def date_picker():
        if not df.empty:
            min_date = df['date'].min()
            max_date = df['date'].max()
            date_range = st.date_input('Date Range', value=(st.session_state.start_date, st.session_state.end_date))
        else:
            today = datetime.datetime.now(ZoneInfo("America/Chicago")).date()
            date_range = st.date_input('Date Range', value=(today, today))
            
        if isinstance(date_range, tuple) and len(date_range) == 2:
            selected_start = date_range[0]
            selected_end = date_range[1]
        else:
            selected_start = date_range
            selected_end = date_range

        if st.button('Apply'):
            st.session_state.start_date = selected_start
            st.session_state.end_date = selected_end
            st.rerun()

    selected_filter = st.pills(label='Filter', label_visibility='collapsed', options=['Today', 'Yesterday', '7 Day', '30 Day', 'Custom'], default='Today',  key='date_filter')

    # today button
    if selected_filter == 'Today':
        start_date = today
        end_date = today

    # yesterday button
    elif selected_filter == 'Yesterday':
        start_date = today - datetime.timedelta(days=1)
        end_date = start_date

    # 7 days button
    elif selected_filter == '7 Day':
        start_date = today - datetime.timedelta(days=6)
        end_date = today

    # 30 days button
    elif selected_filter == '30 Day':
        start_date = today - datetime.timedelta(days=29)
        end_date = today

    # custom button
    elif selected_filter == 'Custom':
        if 'start_date' not in st.session_state:
            st.session_state.start_date = df['date'].min()
            st.session_state.end_date = df['date'].max()

        start_date = st.session_state.start_date
        end_date = st.session_state.end_date

        date_picker()

    if start_date == end_date:
        single_day = True
        st.write(f"**{start_date.strftime('%b %d, %Y').replace(' 0', ' ')}** (CDT)")
    else:
        st.write(f"**{start_date.strftime('%b %d, %Y').replace(' 0', ' ')} - {end_date.strftime('%b %d, %Y').replace(' 0', ' ')}** (CDT)")

    period_length = (end_date - start_date).days + 1
    comparison_end = start_date - datetime.timedelta(days=1)
    comparison_start = comparison_end - datetime.timedelta(days=period_length - 1)

    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)] if not df.empty else pd.DataFrame(columns=df.columns)
    comparison_df = df[(df['date'] >= comparison_start) & (df['date'] <= comparison_end)]

    # current period values
    current_commission = filtered_df['commission'].sum()
    current_gmv = filtered_df['gmv'].sum()
    current_items = filtered_df['items_sold'].sum()
    current_videos = filtered_df['videos'].sum()
    current_views = filtered_df['views'].sum()

    # previous period values
    prev_commission = comparison_df['commission'].sum()
    prev_gmv = comparison_df['gmv'].sum()
    prev_items = comparison_df['items_sold'].sum()
    prev_videos = comparison_df['videos'].sum()
    prev_views = comparison_df['views'].sum()

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
        if comparison_df.empty:
            commission_delta = None
        elif prev_commission == 0 and current_commission > 0:
            commission_delta = 100
        else:
            commission_delta = utils.calc_percent_change(current_commission, prev_commission)

        if filtered_df.empty:
            st.metric('Commission', '$0')
            if not single_day:
                st.metric('Avg. Daily Commission', '$0')
        else:
            st.metric('Commission', f"${current_commission:,.2f}", delta=f'{commission_delta:.2f}%' if commission_delta is not None else None, 
                      delta_color='grey' if commission_delta == 0 else 'normal', border=True)
            if not single_day:
                st.metric('Avg. Daily Commission', f"${filtered_df['commission'].mean():,.2f}", border=True)

    with col2:  # GMV
        if comparison_df.empty:
            gmv_delta = None
        elif prev_gmv == 0 and current_gmv > 0:
            gmv_delta = 100
        else:
            gmv_delta = utils.calc_percent_change(current_gmv, prev_gmv)

        if filtered_df.empty:
            st.metric('GMV', '$0')
            if not single_day:
                st.metric('Avg. Daily GMV', '$0')
        else:
            st.metric('GMV', f"${current_gmv:,.2f}", delta=f'{gmv_delta:.2f}%' if gmv_delta is not None else None, 
                      delta_color='grey' if gmv_delta == 0 else 'normal', border=True)
            if not single_day:
                st.metric('Avg. Daily GMV', f"${filtered_df['gmv'].mean():,.2f}", border=True)

    with col3:  # items sold
        if comparison_df.empty:
            items_delta = None
        elif prev_items == 0 and current_items > 0:
            items_delta = 100
        else:
            items_delta = utils.calc_percent_change(current_items, prev_items)

        if filtered_df.empty:
            st.metric('Items Sold', '0')
            if not single_day:
                st.metric('Avg. Daily Items Sold', '0')
        else:
            st.metric('Items Sold', f"{int(current_items):,}", delta=f'{items_delta:.2f}%' if items_delta is not None else None, 
                      delta_color='grey' if items_delta == 0 else 'normal', border=True)
            if not single_day:
                st.metric('Avg. Daily Items Sold', f"{float(filtered_df['items_sold'].mean()):,.1f}", border=True)

    with col4:  # videos posted
        if comparison_df.empty:
            videos_delta = None
        elif prev_videos == 0 and current_videos > 0:
            videos_delta = 100
        else:
            videos_delta = utils.calc_percent_change(current_videos, prev_videos)

        if filtered_df.empty:
            st.metric('Videos Posted', '0')
            if not single_day:
                st.metric('Avg. Daily Videos Posted', '0')
        else:
            st.metric('Videos Posted', f"{int(current_videos):,}", delta=f'{videos_delta:.2f}%' if videos_delta is not None else None, 
                      delta_color='grey' if videos_delta == 0 else 'normal', border=True)
            if not single_day:
                st.metric('Avg. Daily Videos Posted', f"{float(filtered_df['videos'].mean()):,.1f}", border=True)
    
    with col5:  # views
        if comparison_df.empty:
            views_delta = None
        elif prev_views == 0 and current_views > 0:
            views_delta = 100
        else:
            views_delta = utils.calc_percent_change(current_views, prev_views)

        if filtered_df.empty:
            st.metric('Views', '0')
            if not single_day:
                st.metric('Avg. Daily Views', '0')
        else:
            st.metric('Views', f"{filtered_df['views'].sum():,}", delta=f'{views_delta:.2f}%' if views_delta is not None else None, 
                      delta_color='grey' if views_delta == 0 else 'normal', border=True)
            if not single_day:
                st.metric('Avg. Daily Views', f"{int(filtered_df['views'].mean()):,}", border=True)

    c1, c2, c3 = st.columns(3)

    # display average commission rate and quality
    with c1:
        if filtered_df.empty or filtered_df['gmv'].sum() == 0:
            st.metric('Avg. Commission Rate', '-', border=True)
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

            if comparison_df.empty or comparison_df['gmv'].sum(0) == 0:
                delta = None
            else:
                comparison_c_rate = metrics.avg_commission_rate(comparison_df)
                delta = utils.calc_percent_change(avg_c_rate, comparison_c_rate)

            st.metric('Avg. Commission Rate', f"{avg_c_rate}% - {quality}", delta=f'{delta:.2f}%' if delta is not None else None, border=True)

    # display conversion rate and quality
    with c2:
        if filtered_df.empty or filtered_df['views'].sum() == 0:
            st.metric('Conversion Rate', '-', border=True)
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

            if comparison_df.empty or comparison_df['views'].sum(0) == 0:
                delta = None
            else:
                comparison_conv_rate = metrics.conversion_rate(comparison_df)
                delta = utils.calc_percent_change(conv_rate, comparison_conv_rate)

            st.metric('Conversion Rate', f"{conv_rate}% - {quality}", delta=f'{delta:.2f}%' if delta is not None else None, border=True)

    # display RPM and quality
    with c3:
        if filtered_df.empty or filtered_df['views'].sum() == 0:
            st.metric('RPM', '-', border=True)
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

            if comparison_df.empty or comparison_df['views'].sum(0) == 0:
                delta = None
            else:
                comparison_rpm = metrics.rpm(comparison_df)
                delta = utils.calc_percent_change(rpm, comparison_rpm)

            st.metric('RPM', f'${rpm} - {quality}', delta=f'{delta:.2f}%' if delta is not None else None, border=True)

    if not single_day:

        # commission line chart
        commission_fig = px.line(filtered_df, x='date', y='commission', title='Daily Commission')
        commission_fig.update_traces(line=dict(color='springgreen'))
        commission_fig.update_layout(xaxis=dict(fixedrange=True, title=None), yaxis=(dict(tickprefix='$', fixedrange=True, title=None)), dragmode=False)
        st.plotly_chart(commission_fig, width='stretch', config={'displayModeBar': False, 'staticPlot': False})
    
        # views line chart
        views_fig = px.line(filtered_df, x='date', y='views', title='Daily Views')
        views_fig.update_traces(line=dict(color='royalblue'))
        views_fig.update_layout(xaxis=dict(fixedrange=True, title=None), yaxis=(dict(fixedrange=True, title=None)), dragmode=False)
        st.plotly_chart(views_fig, width='stretch', config={'displayModeBar': False, 'staticPlot': False})

        # GMV line chart
        #gmv_fig = px.line(filtered_df, x='date', y='gmv', title='Daily GMV')
        #gmv_fig.update_traces(line=dict(color='green'))
        #gmv_fig.update_layout(yaxis=(dict(tickprefix='$')))
        #st.plotly_chart(gmv_fig, width='stretch')

        # videos posted line chart
        #items_fig = px.line(filtered_df, x='date', y='videos', title='Daily Videos Posted')
        #items_fig.update_traces(line=dict(color='orange'))
        #st.plotly_chart(items_fig, width='stretch')

### Daily Log tab
with tab2:
    left, right = st.columns([1.75, 1])

    # data input
    with left:
        data_date_input = st.pills(label='Filter', label_visibility='collapsed',  options=['Today', 'Yesterday'], default='Today')

        # display current selected date
        current_date = today
        if data_date_input == 'Yesterday':
            current_date = today - datetime.timedelta(days=1)

        log_contain = st.container(horizontal=True)

        with log_contain:
            current_date = log_contain.date_input(f'Date: {current_date.strftime('%b %d, %Y').replace(' 0', ' ')}', value=current_date)

            commission = utils.float_input('commission', 'Commission', df, current_date)

            gmv = utils.float_input('gmv', 'GMV', df, current_date)

            items_sold = utils.integer_input('items_sold', 'Items Sold', df, current_date)

            videos = utils.integer_input('videos', 'Videos Posted', df, current_date)

            views = utils.integer_input('views', 'Views', df, current_date)

        button_label = 'Save'

    # warns user they are updating an existing entry date
    with st.container(width='content'):
        warning_box = st.empty()
        if utils.date_exists(df, current_date):
            warning_box.info(f'About to update entry for {current_date.strftime('%b %d, %Y').replace(' 0', ' ')}', icon=':material/info_i:')
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
            with st.container(width='content'):
                st.success(f'Saved entry for {current_date.strftime('%b %d, %Y').replace(' 0', ' ')}.', icon=':material/check_circle:')

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
            with st.container(width='content'):
                warning_box.empty()
                st.success(f'Updated entry for {current_date.strftime('%b %d, %Y').replace(' 0', ' ')}', icon=':material/check_circle:')

### Goals tab
with tab3:
    with st.popover('Goal options'):
        months = []
        analytics = ['Commission', 'GMV']

        for i in range(2):
            month_date = today.replace(day=1) + datetime.timedelta(days=32 * i)
            month_date = month_date.replace(day=1)
            months.append(month_date)

        selected_month = st.selectbox('Month', months, format_func=lambda x: x.strftime('%B'))
        selected_analytic = st.selectbox('Analytic', analytics)
        goal_amount = st.number_input('Amount', min_value=0, step=100, format='%d')

        if st.button('Save Goal'):
            database.save_goal(
                connection,
                user_id,
                selected_month,
                selected_analytic,
                goal_amount
            )
            st.rerun()

    goal = database.load_goal(
        connection,
        user_id,
        selected_month,
        selected_analytic,
    )

    temp_date = pd.to_datetime(df['date'])

    analytic_type = selected_analytic.lower()

    current_value = df[(temp_date.dt.year == selected_month.year) & (temp_date.dt.month == selected_month.month)][analytic_type].sum()

    if goal is not None and goal != 0:
        progress = min(current_value / goal, 1.0)
        remaining = max(goal - current_value, 0)
    else: 
        progress = 0
        remaining = 0

    if goal is not None and goal != 0:
        st.markdown(f"### {selected_month.strftime('%B')} {selected_analytic} Goal", anchors=False)

        prog_contain = st.container(horizontal=True)
        with prog_contain:
            st.progress(progress, text=f'Progress - {(progress*100):.0f}%')
            #st.markdown(f'#### {(progress*100):.0f}%', anchors=False)
            st.markdown(f'### ${goal:,.0f}', anchors=False)
        
        goal_contain = st.container(horizontal=True)
        
        #goal_contain.metric('Goal', f'${goal:,.0f}', border=True)
        goal_contain.metric('Current', f'${current_value:,.2f}', border=True)
        goal_contain.metric('Remaining', f'${remaining:,.2f}', border=True)

        days_left = utils.days_left_in_month(selected_month, today)
        if days_left > 0:
            remaining_per_day = remaining / days_left
        else:
            remaining_per_day = remaining

        days_passed = today.day
        monthly_predict = (current_value / days_passed) * (days_left + days_passed)

        if today.month == selected_month.month:
            goal_contain.metric('Projected', f'${monthly_predict:,.2f}', border=True)
        else:
            goal_contain.metric('Projected', '-', border=True)

        if remaining_per_day < 0.01 and not progress == 1.0:
            st.markdown(f"##### Less than $0.01 required per day to complete goal.", anchors=False)
        elif progress == 1.0:
            st.markdown(f"##### {selected_month.strftime('%B')} {selected_analytic} goal completed. Nice work.", anchors=False)
        else:
            st.markdown(f"##### ${remaining_per_day:,.2f}/day required to hit goal.", anchors=False)
            
    else:
        st.markdown('#### No current goal.', anchors=False)

    #st.markdown(f'## **\\${current_value:,.0f} / \\${goal:,.0f}**', anchors=False)

### Data tab
with tab4:
    st.title('All Data', anchor=False)

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