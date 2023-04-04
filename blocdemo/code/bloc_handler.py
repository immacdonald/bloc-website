from django.conf import settings

import os
import osometweet

from argparse import Namespace

from bloc.generator import gen_bloc_for_users
from bloc.subcommands import run_subcommands


def analyze_user(screen_name):
    #users_bloc = gen_bloc_for_users([screen_name], settings.BEARER_TOKEN, '', '', '', '')
    #return users_bloc
    oauth2 = osometweet.OAuth2(bearer_token=settings.BEARER_TOKEN, manage_rate_limits=False)
    ot = osometweet.OsomeTweet(oauth2)
    # Returns dict list with 'id' 'name' and 'username' fields
    user_data = ot.user_lookup_usernames([screen_name])['data']
    user_ids = [ user['id'] for user in user_data ]

    gen_bloc_params, gen_bloc_args = get_bloc_params(user_ids, settings.BEARER_TOKEN, bloc_alphabets=['action', 'content_syntactic', 'content_semantic_entity'])
    bloc_payload = gen_bloc_for_users(**gen_bloc_params)

    all_bloc_output = bloc_payload.get('all_users_bloc', [])
    #total_tweets = sum([ user_bloc['more_details']['total_tweets'] for user_bloc in bloc_payload ])

    pairwise_sim_report = run_subcommands(gen_bloc_args, 'sim', all_bloc_output)
    top_k_bloc_words = run_subcommands(gen_bloc_args, 'top_ngrams', all_bloc_output)

    print('TOP BLOC WORDS', top_k_bloc_words)

    '''pairwise_sim_report = sorted(pairwise_sim_report, key=lambda x: x['sim'], reverse=True)
    print('\nWrote pairwise_sim_report.json. Preview of first 10 most similar user pairs.')
    for i in range(len(pairwise_sim_report[:10])):
        u_pair = pairwise_sim_report[i]
        print('\t{:02d}. {:.3f} {}, {}'.format( i+1, u_pair['sim'], u_pair['user_pair'][0], u_pair['user_pair'][1]) )'''
    
    result = {
        # User Data
        'account_name': user_data[0]['name'],
        # BLOC Statistics
        'tweet_count': all_bloc_output[0]['more_details']['total_tweets'],
        'first_tweet_date': all_bloc_output[0]['more_details']['first_tweet_created_at_local_time'],
        'last_tweet_date': all_bloc_output[0]['more_details']['last_tweet_created_at_local_time'],
        'elapsed_time': all_bloc_output[0]['elapsed_time']['gen_tweets_total_seconds'] + all_bloc_output[0]['elapsed_time']['gen_bloc_total_seconds'],
        # Analysis
        'bloc_action': all_bloc_output[0]['bloc']['action'],
        'bloc_content_syntactic': all_bloc_output[0]['bloc']['content_syntactic'],
        'bloc_content_semantic': all_bloc_output[0]['bloc']['content_semantic_entity'],
        'top_bloc_words': top_k_bloc_words['per_doc'][0]
    }

    return result



def get_bloc_params(user_ids, bearer_token, token_pattern='word', no_screen_name=True, account_src='Twitter search', no_sleep=True, max_pages=1, max_results=100, bloc_alphabets = ['action', 'content_syntactic']):
    #bloc_alphabets = ['action', 'change', 'content_syntactic', 'content_semantic_entity', 'content_semantic_sentiment']
    params = {
        'screen_names_or_ids': user_ids, 
        'bearer_token': bearer_token, 
        'account_src': account_src,
        'account_class': '',
        'access_token': '', 'access_token_secret': '', 'consumer_key': '', 'consumer_secret': '', 
        'blank_mark': 60, 'minute_mark': 5, 'segmentation_type': 'week_number', 'days_segment_count': -1, 
        'ansi_code': '91m', 
        'bloc_alphabets': bloc_alphabets, 'bloc_symbols_file': None, 
        'cache_path': '', 'cache_read': False, 'cache_write': False, 
        'following_lookup': False, 
        'keep_tweets': False, 
        'keep_bloc_segments': False, 
        'log_file': '', 'log_format': '', 'log_level': 'INFO', 'log_dets': {'level': 20},
        'max_pages': max_pages, 'max_results': max_results, 
        'no_screen_name': no_screen_name, 'no_sleep': no_sleep, 
        'output': None, 
        'timeline_startdate': '', 'timeline_scroll_by_hours': None, 'time_function': 'f2', 
        'subcommand': '', 

        'fold_start_count': 4,
        'keep_tf_matrix': False,
        'ngram': 1 if token_pattern == 'word' else 2,
        'sort_action_words': False,#
        'set_top_ngrams': False,
        'tf_matrix_norm': '',
        'token_pattern': token_pattern,
        'top_ngrams_add_all_docs': False,
        'sim_no_summary': True,
        'tweet_order': 'reverse'
    }

    return params, Namespace(**params)