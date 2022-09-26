import os
import mne
import pandas as pd
import numpy as np
import csv

MAX_PEAK2PEAK = 100e-6
N250_RANGE = [0.23, 0.32] # 实验一
N250_RANGE_EXP2 = [0.21, 0.26] # 实验二
N170_RANGE = [0.11, 0.19]

N170_Channel = ['P7','PO7','P8','PO8']

HEMISPHERES = {'left': ['TP9', 'P7', 'PO7',  'O1'],
               'right': ['TP10', 'P8', 'PO8' , 'O2']}

condition_list = ['OtherFace_1',
 'OtherFace_2',
 'OtherFace_3',
 'OtherFace_4',
 'OtherFace_5',
 'OtherFace_6',
 'OtherFace_7',
 'OtherFace_8',
 'OtherFace_9',
 'OtherFace_10',
 'OwnFace',
 'JoeFace']

Sublist_exp1_ica = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30',\
    '31','32','33','34','35','36','37','38','39','40']

exp1_bad = {'9' : 'FT9', '13' : 'FC2', '36' : 'pass'}

exp1_rejected  = ['3','4', '7','16','20','30','36']
# sub 9 should be reanalized.


Sublist_exp1 = ['1','2','5','6','8','9','10','11','12','13','14','15','17','18','19','21','22','23','24','25','26','27','28','29',\
    '31','32','33','34','35','37','38','39','40']


Sublist_exp2_ica = ['1','2','3','4','5','6','7','8','10','11','12','13','14','15','16','17']
Sublist_exp2 = ['1','3','4','5','7','8','11','12','13','15','17']
exp2_bad = {
    '5' : 'AF8', 
    '6' : 'AF8', 
    '7' : 'AF8',
    '8':['AF8','C2'],
    '10':['AF8', 'C2'],
    '11':['O2', 'CPz','AF8'],
    '12':['AF8','C2'],
    '13':['P2', 'CPz', 'AF8', 'AF4'],
    '14':['P2','CPz','FT8','AF8','AF4','TP8'],
    '16':['AF8','AF4'],
    '17':['AF8', 'TP10']
    }




eventdict_1 = {
    'OtherFace_1': 10,
    'OtherFace_2': 12,
    'OtherFace_3' : 13,
    'OtherFace_4' : 14,
    'OtherFace_5' : 15,
    'OtherFace_6' : 16,
    'OtherFace_7' : 17,
    'OtherFace_8' : 18,
    'OtherFace_9' : 19,
    'OtherFace_10' : 11,
    'OwnFace' : 22,
    'JoeFace' : 33,
            }


def make_relax_annotations(rawfile):
    events, eventid = mne.events_from_annotations(rawfile)
    events_df = pd.DataFrame(events)

    relax_start = []
    relax_end = []

    for i in events_df.index[1:]:
        if events_df.iloc[i, 0] - events_df.iloc[i - 1, 0] > 4500:
            relaxtime_start = events_df.iloc[i - 1, 0]
            relaxtime_end = events_df.iloc[i, 0]

            # 将start与end时间点加入list中
            relax_start.append(relaxtime_start)
            relax_end.append(relaxtime_end)

    # 转化为数组方便计算
    relax_start = np.asarray(relax_start)
    relax_end = np.asarray(relax_end)

    # start & end各自加减100ms以避开marker，随后计算duration
    relax_start = relax_start + 100
    relax_end = relax_end - 100
    relax_duration = relax_end - relax_start

    # caculate onset & duration in seconds
    relax_onset = relax_start / 1000
    relax_duration = relax_duration / 1000

    bad_relax_annot = mne.Annotations(onset=relax_onset, duration=relax_duration, description="Bad_relax",
                                      orig_time=rawfile.info['meas_date'])
    return bad_relax_annot


def crop_raw_relax(rawfile):
    event, eventid = mne.events_from_annotations(rawfile)
    event_df = pd.DataFrame(event)
    last_marker_time = (event_df.iloc[event_df.index.max(),0] + 3000) / 1000
    rawfile.crop(tmin = 0, tmax = last_marker_time)


def get_corrected_events(events):
    events_df = pd.DataFrame(events)
    for ind in events_df.index[1:]:
        if events_df.loc[ind].values[2] == 2:
            events_df.drop([ind], inplace=True)
            events_df.drop([ind - 1], inplace=True)

    for ind in events_df.index[1:]:
        if events_df.loc[ind].values[2] == 3:
            events_df.drop([ind], inplace=True)
            events_df.drop([ind - 1], inplace=True)

    for ind in events_df.index[1:]:
        if events_df.loc[ind].values[2] == 1:
            events_df.drop([ind], inplace=True)

    for ind in events_df.index:
        if events_df.loc[ind].values[2] == 99999:
            events_df.drop([ind], inplace=True)

    for ind in events_df.index:
        if events_df.loc[ind].values[2] == 10001:
            events_df.drop([ind], inplace=True)

    for ind in events_df.index:
        if events_df.loc[ind].values[2] == 10003:
            events_df.drop([ind], inplace= True)
    
    for ind in events_df.index:
        if events_df.loc[ind].values[2] == 10002:
            events_df.drop([ind], inplace= True)

    corrected_events = events_df.values
    return corrected_events

def crop_raw_1third_v2(events):
    sumed_trial_numbers = events.shape[0]
    one_third_event_numbers = int(np.floor(sumed_trial_numbers/3))
    one_third_events = events[:one_third_event_numbers,:]
    two_third_events = events[one_third_event_numbers:,:]

    return one_third_events,two_third_events

def crop_raw_1two(events):
    sumed_trial_numbers = events.shape[0]
    one_two_event_numbers = int(np.floor(sumed_trial_numbers/2))
    one_two_events = events[:one_two_event_numbers,:]
    two_two_events = events[one_two_event_numbers:,:]

    return one_two_events, two_two_events

def calculate_n250_avg(n250_epochs):
    avg_list = []
    for col in n250_epochs.columns:
        avg_n250 = n250_epochs[col].mean()
        avg_list.append(avg_n250)
    print(len(avg_list))
    n250_averaged = pd.DataFrame(columns= n250_epochs.columns)
    n250_averaged.loc[0] = avg_list
    return n250_averaged

def calculate_250_by_hemi(averaged_n250, direction):
    electrodes = list(HEMISPHERES[direction])
    print(electrodes)
    df_for_calculate = averaged_n250[electrodes]
    print(df_for_calculate)
    mean_n250_allelectrodes = df_for_calculate.loc[0].mean()
    print(direction + ':' + str( mean_n250_allelectrodes))
    return mean_n250_allelectrodes
    
def calculate_N250(first_epoch, second_epoch):

    """
    
    Input - first epoch(mne.epoch), second epoch
    Return - A dictionary of averaged N250 for 6 condition: 1_left, 1_right, 2_left, 2_right, 1_avg, 2_avg
    
    """

    result_dict = {}


    #### JoeFace#####

    #Joe_first, Joe_second - type: epochs
    Joe_first = first_epoch['JoeFace']
    Joe_second = second_epoch['JoeFace']
    Joe_first_df = Joe_first.to_data_frame()
    Joe_second_df = Joe_second.to_data_frame()

    # extract N250 time window from epochs's dataframe
    Joe_first_250 = Joe_first_df[(Joe_first_df['time'] > 230) & (Joe_first_df['time'] < 320)].iloc[:,3:]
    Joe_second_250 = Joe_second_df[(Joe_second_df['time'] > 230) & (Joe_second_df['time'] < 320)].iloc[:,3:]

    # Joe_first_avg - type: dataframe, shape(1,63), return from function(calculate_n250_avg)
    Joe_first_avg = calculate_n250_avg(Joe_first_250)
    Joe_second_avg = calculate_n250_avg(Joe_second_250)


    Joe_first_left = calculate_250_by_hemi(Joe_first_avg, direction= 'left')
    Joe_first_right = calculate_250_by_hemi(Joe_first_avg, direction= 'right')

    Joe_second_left = calculate_250_by_hemi(Joe_second_avg, direction= 'left')
    Joe_second_right = calculate_250_by_hemi(Joe_second_avg, direction= 'right')

    Joe_first_averaged = (Joe_first_left + Joe_first_right)/2
    Joe_second_averaged = (Joe_second_left + Joe_second_right)/2

    result_dict['Joe_1_left'] = Joe_first_left
    result_dict['Joe_2_left'] = Joe_second_left
    result_dict['Joe_1_right'] = Joe_first_right
    result_dict['Joe_2_right'] = Joe_second_right
    result_dict['Joe_1_avg'] = Joe_first_averaged
    result_dict['Joe_2_avg'] = Joe_second_averaged


    #### Own Face ####
    Own_first = first_epoch['OwnFace']
    Own_second = second_epoch['OwnFace']
    Own_first_df = Own_first.to_data_frame()
    Own_second_df = Own_second.to_data_frame()

    Own_first_250 = Own_first_df[(Own_first_df['time'] > 230) & (Own_first_df['time'] < 320)].iloc[:,3:]
    Own_second_250 = Own_second_df[(Own_second_df['time'] > 230) & (Own_second_df['time'] < 320)].iloc[:,3:]

    Own_first_avg = calculate_n250_avg(Own_first_250)
    Own_second_avg = calculate_n250_avg(Own_second_250)

    Own_first_left = calculate_250_by_hemi(Own_first_avg, direction= 'left')
    Own_first_right = calculate_250_by_hemi(Own_first_avg, direction= 'right')
    Own_second_left = calculate_250_by_hemi(Own_second_avg, direction= 'left')
    Own_second_right = calculate_250_by_hemi(Own_second_avg, direction= 'right')

    Own_first_averaged =( Own_first_left + Own_first_right) /2
    Own_second_averaged =(Own_second_left + Own_second_right) /2

    result_dict['Own_1_left'] = Own_first_left
    result_dict['Own_2_left'] = Own_second_left
    result_dict['Own_1_right'] = Own_first_right
    result_dict['Own_2_right'] = Own_second_right
    result_dict['Own_1_avg'] = Own_first_averaged
    result_dict['Own_2_avg'] = Own_second_averaged

    ### Other Face -1 ###

    

    Other_first = first_epoch['OtherFace_1']
    Other_second = second_epoch['OtherFace_1']
    Other_first_df = Other_first.to_data_frame()
    Other_second_df = Other_second.to_data_frame()

    Other_first_250 = Other_first_df[(Other_first_df['time'] > 230) & (Other_first_df['time'] < 320)].iloc[:,3:]
    Other_second_250 = Other_second_df[(Other_second_df['time'] > 230) & (Other_second_df['time'] < 320)].iloc[:,3:]

    Other_first_avg = calculate_n250_avg(Other_first_250)
    Other_second_avg = calculate_n250_avg(Other_second_250)

    Other_first_left = calculate_250_by_hemi(Other_first_avg, direction= 'left')
    Other_first_right = calculate_250_by_hemi(Other_first_avg, direction= 'right')

    Other_second_left = calculate_250_by_hemi(Other_second_avg, direction= 'left')
    Other_second_right = calculate_250_by_hemi(Other_second_avg, direction= 'right')

    Other_first_averaged = (Other_first_left + Other_first_right)/2
    Other_second_averaged = (Other_second_left + Other_second_right)/2

    result_dict['Other_1_left'] = Other_first_left
    result_dict['Other_2_left'] = Other_second_left
    result_dict['Other_1_right'] = Other_first_right
    result_dict['Other_2_right'] = Other_second_right
    result_dict['Other_1_avg'] = Other_first_averaged
    result_dict['Other_2_avg'] = Other_second_averaged

    return result_dict

def get_n250_time_series(epoch, type = 'JoeFace'):
    N250_TS_dict = {}
    target_epoch = epoch['JoeFace']
    cropped_target_epochs = target_epoch.crop(N250_RANGE[0], N250_RANGE[1]).to_data_frame()
    for epoch in cropped_target_epochs.epoch.value_counts().index:
        single_epoch_for_N250 = cropped_target_epochs[cropped_target_epochs['epoch'] == epoch][['TP10','P8','PO8','O2','TP9','P7','PO7','O1']].mean()
        N250_TS_dict[epoch] = single_epoch_for_N250
    Sub_N250_TS = pd.DataFrame(N250_TS_dict).T.sort_index()
    Sub_N250_TS['Right_Avg'] = (Sub_N250_TS['PO8'] + Sub_N250_TS['P8'] + Sub_N250_TS['TP10'] + Sub_N250_TS['O2'])/4
    Sub_N250_TS['Left_Avg'] = (Sub_N250_TS['P7'] + Sub_N250_TS['PO7'] +Sub_N250_TS['TP9'] + Sub_N250_TS['O1'])/4
    Sub_N250_TS['LR_Avg'] = (Sub_N250_TS['PO8'] + Sub_N250_TS['P8'] + Sub_N250_TS['P7'] + Sub_N250_TS['PO7'] + Sub_N250_TS['TP10']  + Sub_N250_TS['O2'] + \
        Sub_N250_TS['TP9'] + Sub_N250_TS['O1'] )/8

    return Sub_N250_TS

def Calculate_latency_and_amplitude(type, data):
    if type == 'N170':
        N170_amplitude_dict = {}
        N170_latency_dict = {}
        for ch in N170_Channel:
            data_in_window = data.iloc[310:391,:]
            latency = data_in_window.loc[data_in_window[ch].idxmin()][0]
            Amplitude = data_in_window[ch].min()
            N170_amplitude_dict[ch] = Amplitude
            N170_latency_dict[ch] = latency
        return N170_amplitude_dict, N170_latency_dict
    elif type == 'N250':
        N250_amplitude_dict = {}
        for ch in HEMISPHERES['left']:
            data_in_window = data.iloc[410:460,:]
            Amplitude = data_in_window[ch].mean()
            N250_amplitude_dict[ch] = Amplitude
        for ch in HEMISPHERES['right']:
            N250_data = data.iloc[410:460,:]
            Amplitude = N250_data[ch].mean()
            N250_amplitude_dict[ch] = Amplitude
        return N250_amplitude_dict


def get_rt_time(events):

    '''
    input: events from raw annotations
    output: a list of reaction time
    '''

    reaction_time_list = []
    events_df = pd.DataFrame(events,columns= ['Time','Filler','Marker'])
    for line in events_df.index:
        if events_df.iloc[line,2] == 1:
            reaction_time = (events_df.iloc[line,0] - events_df.iloc[line-1, 0]) - 1000
            reaction_time_list.append(reaction_time)
    
    return reaction_time_list