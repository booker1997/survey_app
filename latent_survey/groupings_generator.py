import pandas as pd
import random
import numpy as np

needs_dict = pd.read_csv('data/raw_needs.csv')
needs_vacuum = [need for need in list(needs_dict['Need (vacuum)']) if type(need) == str ]
needs_desk = [need for need in list(needs_dict['Need (Desk)']) if type(need) == str ]




def make_fully_random_groups(desk_or_vacuum, times_each_need_needs_to_be_seen,grouping_size):
    if desk_or_vacuum == 'desk':
        final_file_name = 'need_groups_desk.csv'
        need_list = needs_desk
    else:
        final_file_name = 'need_groups_vacuum.csv'
        need_list= needs_vacuum

    need_count_dict = {need:0 for need in need_list}

    groups_dict = {}
    group_i = 1
    while sum(need_count_dict.values())< len(need_list)*times_each_need_needs_to_be_seen:
        # Filter the list according to the condition
        filtered_lst = [need for need in need_list if need_count_dict[need]<times_each_need_needs_to_be_seen]

        # Choose n random values from the filtered list
        n = grouping_size  # Change this to the number of values you want
        if len(filtered_lst) < n:
            n = len(filtered_lst)
        chosen_values = random.sample(filtered_lst, n)
        
        for need in chosen_values:
            need_count_dict[need] += 1
        print(len(chosen_values))
        if len(chosen_values)<grouping_size:
            padding = np.zeros(grouping_size-len(chosen_values))
            chosen_values += list(padding)
        groups_dict[f'group {group_i}'] = chosen_values

        group_i += 1

    for ne in need_count_dict:
        if need_count_dict[ne] != times_each_need_needs_to_be_seen:
            print('PROBLEM',ne,need_count_dict[ne])
    groups_df = pd.DataFrame(groups_dict)
    groups_df.to_csv(final_file_name)
    print(groups_df)

def make_groups_split_whole_in_two(desk_or_vacuum,n_repeat):
    if desk_or_vacuum == 'desk':
        final_file_name = 'need_groups_desk.csv'
        need_list = np.array(needs_desk)
    else:
        final_file_name = 'need_groups_vacuum.csv'
        need_list= np.array(needs_vacuum)
    
    print(len(need_list))
    half_length = int((len(need_list))/2)
    groups_dict = {}
    for i in range(0,n_repeat):
        need_indexes = list(range(0,len(need_list)))
        random.seed(i)
        random.shuffle(need_indexes)
        first_group_i = need_indexes[:half_length]
        second_group_i= need_indexes[half_length:]
        if len(first_group_i) != len(second_group_i):
            groups_dict[f'Group {i+1}a'] = list(need_list[first_group_i])+ [0]
            groups_dict[f'Group {i+1}b'] = list(need_list[second_group_i]) 
        else:
            groups_dict[f'Group {i+1}a'] = list(need_list[first_group_i])
            groups_dict[f'Group {i+1}b'] = list(need_list[second_group_i]) 
       

        groups_df = pd.DataFrame(groups_dict)
        groups_df.to_csv(final_file_name)
        print(groups_df)


    

# desk_or_vacuum = 'vacuum'
desk_or_vacuum = 'desk'
times_each_need_needs_to_be_seen = 3
grouping_size = 56

# make_fully_random_groups(desk_or_vacuum,times_each_need_needs_to_be_seen,grouping_size)

make_groups_split_whole_in_two(desk_or_vacuum,n_repeat=3)