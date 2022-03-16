import eel
import pandas as pd

# print(sys.version)
# print(sys.executable)

eel.init('web')


@eel.expose
def hello_eel():
    return 'You clicked the button'

@eel.expose
def read_data():
    df = pd.read_excel('test.xlsx')
    # print(df.to_html())
    return df.to_html()

@eel.expose
def get_date_js(dt):
    print(dt)
    print(type(dt))

# eel.say_hello_js('python is calling you...JS')



eel.start('index.html')
# hello_eel('llllll')
# # eel.say_hello_js('Shantong\'s Mac')

# eel.start('index.html',size=(300,200),port=5001)
