import pandas as pd
import streamlit as st

def sort_df_by_date(df):
    ''' 
    Takes a dataframe as an argument.
    Returns sorted dataframe.
    '''
    df['date'] = pd.to_datetime(df['date']).dt.date
    df = df.sort_values(by='date')
    return df

def load_data(connection):
    '''
    Loads all dat from SQLite database.
    Returns sorted dataframe.
    '''
    query = 'SELECT * FROM daily_stats'
    
    df = pd.read_sql_query(query, connection)

    if df.empty:
        return pd.DataFrame(columns = [
            'date',
            'commission',
            'gmv',
            'items_sold',
            'videos',
            'views'
        ])
    
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    return sort_df_by_date(df)

def date_exists(df, date):
    '''
    Takes dataframe and date as arguements.
    Returns true if date exists in dateframe.
    '''
    return str(date) in df['date'].astype(str).values

def row_lookup(df, date):
    '''
    Takes dataframe and date as arguements.
    Returns row for given date.
    '''
    return df.loc[df['date'].astype(str) == str(date)].iloc[0]

def get_max_row(df, label):
    '''
    Takes a dataframe and a column label as arguements.
    Returns row that contains maximum value in given column.
    '''
    return df.loc[df[label].idxmax()]

def float_input(column, label, df, date):
        '''
        Args: column(string), label(string), df, date
        Takes a float as input.
        Returns input as float with given label.
        '''
        default = 0.0
        if date_exists(df, date):
            row = row_lookup(df, date)
            default = row[column]
        value = float(st.number_input(label, value=default, key=f'{column}_{date}'))
        st.write(f'{label}: ${value:,.2f}')
        return value

def integer_input(column, label, df, date):
    '''
    Args: column(string), label(string), df, date
    Takes an integer as input.
    Returns input as integer with given label.
    '''
    default = 0
    if date_exists(df, date):
        row = row_lookup(df, date)
        default = row[column]
    value = int(st.number_input(label, value=default, key=f'{column}_{date}'))
    st.write(f'{label}: {value:,}')
    return value