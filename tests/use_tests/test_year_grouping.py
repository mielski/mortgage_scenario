import pandas as pd

index = pd.RangeIndex(0, 24)

columns = ['amount', 'payment', 'amount_end']

pd.DataFrame(index=index, columns=columns)

