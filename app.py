import eel
import pandas as pd
import numpy as np
import glob
import Daily_Check_Function_book as fb


eel.init('web',allowed_extensions=['.js','.html'])
eel.start('index.html',block=False)



#write greeting words in python and let JS call the function
@eel.expose
def greeting():
    a = 'Hello Shantong, greeting from Python to JS'
    return a

#recieve nav dates from JS
# @eel.expose
# def sendNavDate(nav_date):
#     print(f'the nave date python collect is {nav_date}')

@eel.expose
def read_data():
    df = pd.read_excel('test.xlsx')
    # print(df.to_html())
    return df.to_html()



@eel.expose
def sendNavDate(nav_date):
    df = pd.read_excel('test.xlsx')
    df['navDate'] = np.nan
    df['navDate'] = nav_date
    df.to_excel('test_result.xlsx')
    return df.to_html()

@eel.expose
def to_files():
    return eel.go_to('/files.html')()

#check if EFA files are ready
@eel.expose
def check_files(file_name,nav_date):
    'test_csv/ffnav1_740666_70258119_28022022_multi_1.csv'
    'test_csv/ffpos1_324307_70248356_28022022_021412_1.csv'
    if file_name == 'ffnav':
        file_pattern = 'test_csv/ffnav1_*_*_' + nav_date + '_multi_1.csv'
    elif file_name == 'ffpos':
        file_pattern = 'test_csv/ffpos1_*_*_' + nav_date + '_*_1.csv'
    else:
        pass

    if len(glob.glob(file_pattern))>0:
        # return f'File exist: {file_name}, {nav_date}.' + u'\N{check mark}'
        print(u'\u2705')
        return u'\u2705'
    else:
        print(u'\u274C')
        return u'\u274C'

#find files..
def find_ffpos(sub_acc):
    ffpos_file_path = fb.file_directory_generator("ffpos", report_date, sub_acc)
    file_name_list = glob.glob(ffpos_file_path)
    assert (
        len(file_name_list) > 0
    ), f"The FFPOS file on {report_date_strf} for {sub_acc} is not in the folder, could you double check!!!"
    
    return file_name_list[0]

t=0
while True:
    eel.sleep(1)
    # print(f'eel running for {t} seconds')
    # t+=1

