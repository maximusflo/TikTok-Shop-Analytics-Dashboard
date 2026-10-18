def avg_commission_rate(df):
    '''
    Calculates average commission rate.
    '''
    total_commission = df['commission'].sum()
    total_gmv = df['gmv'].sum()

    if total_gmv == 0:
        return 0
    
    commission_rate = total_commission / total_gmv * 100
    return round(commission_rate, 1)

def conversion_rate(df):
    '''
    Calculates conversion rate.
    '''
    conversions = df['items_sold'].sum()
    views = df['views'].sum()

    if views == 0:
        return 0

    conv_rate = conversions / views * 100
    return round(conv_rate, 4)

def views_per_item_sold(df):
    '''
    Calculates the number of views per one item sold.
    '''
    views = df['views'].sum()
    items = df['items_sold'].sum()

    if items == 0:
        return 0

    veiws_per_item = views / items
    return int(veiws_per_item)

def rpm(df):
    '''
    Calculates commission per 1,000 views.
    '''
    commission = df['commission'].sum()
    views = df['views'].sum()

    if views == 0:
        return 0
    
    rpm = commission / views * 1000
    return round(rpm, 2)