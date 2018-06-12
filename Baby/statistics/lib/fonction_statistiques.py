#!/usr/bin/python
#coding: utf8

import pandas as pd


################## functions #############################
##########################################################
def time_function(df):
    df['time_goal'] = pd.to_datetime(df['time_goal'])
    df = df.groupby('id_match', as_index=False).agg(['min','max'])['time_goal']
    df['time_start'] = pd.to_datetime(df['min'])
    df['time_end'] = pd.to_datetime(df['max'])

    df['time_duration'] = df['time_end'] - df['time_start']
    df['time_duration'] = df['time_duration'].dt.total_seconds().astype(int)
    col_keep = ['time_start','time_end','time_duration']
    return df[col_keep]


def players_function(df):
    # players count
    df['players_count_dom'] = df[['b1','b2']].count(axis=1)
    df['players_count_ext'] = df[['r1','r2']].count(axis=1)
    df['players_count_all'] = df[['b1','b2','r1','r2']].count(axis=1)
    # players list
    df['players_list_all'] = df['b1'].astype(str)+'-'+df['b2'].astype(str)+'-'+df['r1'].astype(str)+'-'+df['r2'].astype(str)
    df['players_list_dom'] = df['b1'].astype(str)+'-'+df['b2'].astype(str)
    df['players_list_ext'] = df['r1'].astype(str)+'-'+df['r2'].astype(str)
    df = df.groupby('id_match', as_index=False).agg(['max'])
    # keep columns and drop level
    df.columns = df.columns.droplevel(1)
    col_keep = ['players_count_all','players_count_dom','players_count_ext','players_list_all','players_list_dom','players_list_ext']
    df = df[col_keep]
    return df


def results_function(df):
    # create 2 dataframe for domicile and ext winner with filter. Traitments and concat two DF
    # if team domicile win : filter match with domicile winner
    # filter each dataframe for winners domicile or ext

    df_dom_win = df[df.score_b==10]
    df_ext_win = df[df.score_r==10]
    # if dom. team win :
    df_dom_win['winner_loc'] = 'domicile'
    df_dom_win['winner_id1'] = df_dom_win[['b1','b2']].min(axis=1)
    df_dom_win['winner_id2'] = df_dom_win[['b1','b2']].max(axis=1)
    df_dom_win['loser_id1'] = df_dom_win[['r1','r2']].min(axis=1)
    df_dom_win['loser_id2'] = df_dom_win[['r1','r2']].max(axis=1)
    df_dom_win['winners_list_id'] = df_dom_win['winner_id1'].astype(str)+ '-' + df_dom_win['winner_id2'].astype(str)
    df_dom_win['losers_list_id'] = df_dom_win['loser_id1'].astype(str) + '-' + df_dom_win['loser_id2'].astype(str)
    df_dom_win['goal_winner'] = 10
    df_dom_win['goal_loser'] = df_dom_win[['score_r']]
    df_dom_win['goal_difference'] = 10 - df_dom_win[['score_r']]
    df_dom_win.reset_index()
    #if ext. team win :
    df_ext_win['winner_loc'] = 'exterieur'
    df_ext_win['winner_id1'] = df_ext_win[['r1','r2']].min(axis=1)
    df_ext_win['winner_id2'] = df_ext_win[['r1','r2']].max(axis=1)
    df_ext_win['loser_id1'] = df_ext_win[['b1','b2']].min(axis=1)
    df_ext_win['loser_id2'] = df_ext_win[['b1','b2']].max(axis=1)
    df_ext_win['winners_list_id'] = df_ext_win['winner_id1'].astype(str)+ '-' + df_ext_win['winner_id2'].astype(str)
    df_ext_win['losers_list_id'] = df_ext_win['loser_id1'].astype(str) + '-' + df_ext_win['loser_id2'].astype(str)
    df_ext_win['goal_winner'] = 10
    df_ext_win['goal_loser'] = df_ext_win[['score_b']]
    df_ext_win['goal_difference'] = 10 - df_ext_win[['score_b']]
    df_ext_win.reset_index()
    # concat two dataframe
    df_concat = pd.concat([df_dom_win,df_ext_win],axis=0).set_index('id_match').sort_index()
    df_concat = df_concat.drop(['b1','b2','r1','r2','score_b','score_r'],axis=1)
    return df_concat
