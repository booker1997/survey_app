import pandas as pd

groups_dict_vacuum = pd.read_csv('data/need_groups_vacuum.csv')
groups_dict_desk = pd.read_csv('data/need_groups_desk.csv')
groups_dicts = [groups_dict_desk,groups_dict_vacuum]
video_names = ['desk','vacuum']
links_dict_online = {'desk':[],'vacuum':[]}
links_dict_local = {'desk':[],'vacuum':[]}
for i,current_dict in enumerate(groups_dicts):
    groups = list(current_dict.columns)
    name = video_names[i]
    groups.pop(0)
    for j,group in enumerate(groups):
        links_dict_online[name].append(f'https://ideation.pythonanywhere.com/{name}/{j}/instructions')
        links_dict_local[name].append(f'http://127.0.0.1:5000/{name}/{j}/instructions')

links_df = pd.DataFrame()
links_df['desk_local'] = links_dict_local['desk']
links_df['desk_online'] = links_dict_online['desk']
links_df['vacuum_local'] = links_dict_local['vacuum']
links_df['vacuum_online'] = links_dict_online['vacuum']
links_df.to_csv('data/links_for_survey.csv')
print(links_df.head())