import streamlit as st
from sqlalchemy import text

def get_connection():
    return st.connection('postgresql', type='sql')

def save_goal(connection, user_id, month, analytic, goal):
    query = text('''
        INSERT INTO monthly_goals (user_id, month, analytic, goal)
        VALUES (:user_id, :month, :analytic, :goal)
        ON CONFLICT (user_id, month, analytic)
        DO UPDATE SET goal = EXCLUDED.goal
    ''')

    with connection.session as session:
        session.execute(
            query,
            {
                'user_id': user_id,
                'month': month,
                'analytic': analytic,
                'goal': goal
            }
        )
        session.commit()

def load_goal(connection, user_id, month, analytic):
    query = '''
        SELECT goal
        FROM monthly_goals
        WHERE user_id = :user_id
        AND month = :month
        AND analytic = :analytic
    '''

    result = connection.query(
        query,
        params={
            'user_id': user_id,
            'month': month,
            'analytic': analytic
        },
        ttl=0
    )

    if result.empty:
        return None

    return result.iloc[0]['goal']

def is_authorized_user(connection, user_id):
    query = '''
        SELECT 1
        FROM authorized_users
        WHERE user_id = :user_id
    '''

    result = connection.query(
        query,
        params={'user_id': user_id},
        ttl=0
    )

    return not result.empty