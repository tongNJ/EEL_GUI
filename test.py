import pandas as pd

df = pd.read_excel('test.xlsx')
print(df)
print(df.to_html())