
def classic(*loans):

    df_list = []
    for l in loans:
        df = pd.DataFrame((period for period in l)).set_index('period').\
            drop(columns='remaining')
        df_list.append(df)

    return sum(df_list)

def houseprice():
    return 640000.
