#### 
import os
import numpy as np 
from datetime import datetime, timedelta

server_address = 'localhost'
server_username = 'USERNAME'

scenario_name = 'release_20111130-lite'
dir_name = '/Volumes/2TB_NETWORK/Network/Datasets/' + scenario_name + '/'
ssh_ldap_filename = dir_name + 'LDAP/2009-12.csv'
ssh_logon_filename = dir_name + 'logon.csv'
ssh_device_filename = dir_name + 'device.csv'
ssh_email_filename = dir_name + 'email.csv'
ssh_web_filename = dir_name + 'http.csv'
#ssh_file_filename = dir_name + 'file.csv'
ssh_files = [ssh_logon_filename, ssh_device_filename, ssh_email_filename, ssh_web_filename]#, ssh_file_filename]
date_time_format = "%m/%d/%Y %H:%M:%S"
start_date = datetime(2010, 1, 4, 0, 0, 0)
end_date = datetime(2011, 6, 1, 0, 0, 0)

current_date = datetime(2010, 1, 4, 0, 0, 0)
previous_date = datetime(2010, 1, 4, 0, 0, 0)
start_date_for_detection =datetime(2010, 1, 11, 0, 0, 0)


parse_cmu_records = True

user_col = 0
datetime_col = 1
device_col = 2
activity_col = 3

# Feature reduction methods
use_pca_assess = True
use_pca_assess_prior = False
use_std_assess = False
use_entropy_assess = False
use_covariance_assess = False
use_correlation_assess = False


# Classification methods
classify_std = True
classify_value = False
classify_mahal = True
classify_mahal_std = False
classify_cov = False
classify_ocsvm = False
classify_kmeans = False
cumul_score_class = False
compute_entropy = False
classify_using_pca = False
distance_measure_on_raw = False
classify_med_std = False


#### END OF FILENAME PARAMETERS 

# This sets the start date for observation (could also use today's date if setting to run in real time)

#start_date = datetime.today()




update_va = True
use_multiple_anomaly_scores = True
include_new_to_features = True
include_time_in_feature_vector = True
show_all_features_on_plot = False
plot_detail = 24

use_wp5 = False


state = ['today_observation', 'previous_observation', 'alert_observation'] #
ac = ['logon',  'logoff', 'usb_insert', 'usb_remove', 'email', 'http', 'file']
anomaly_types = ['this', 'any', 'new', 'current', 'previous', 'hourly', 'daily', 'user', 'role']
anomaly_description = []
for a in ac:
    anomaly_description.append(a + '_anomaly')
for at in anomaly_types:
    anomaly_description.append(at + '_anomaly')
anomaly_description.append('total_anomaly')



feature_description = {}
feature_description['current_devices_for_user'] = 0
feature_description['current_activities_for_user'] = 0
feature_description['current_attributes_for_user'] = 0
feature_description['current_devices_for_role'] = 0
feature_description['current_activities_for_role'] = 0
feature_description['current_attributes_for_role'] = 0
feature_description['previous_devices_for_user'] = 0
feature_description['previous_activities_for_user'] = 0
feature_description['previous_attributes_for_user'] = 0
feature_description['previous_devices_for_role'] = 0
feature_description['previous_activities_for_role'] = 0
feature_description['previous_attributes_for_role'] = 0
feature_description['new_devices_for_user'] = 0
feature_description['new_devices_for_role'] = 0
feature_description['new_activities_for_this_device_for_user'] = 0
feature_description['new_activities_for_this_device_for_role'] = 0
feature_description['new_attributes_for_this_device_for_user'] = 0
feature_description['new_attributes_for_this_device_for_role'] = 0
feature_description['new_activities_for_any_device_for_user'] = 0
feature_description['new_activities_for_any_device_for_role'] = 0
feature_description['new_attributes_for_any_device_for_user'] = 0
feature_description['new_attributes_for_any_device_for_role'] = 0
for i in range(plot_detail):
    feature_description['hourly_usage_' + str(i)] = 0
for activity in ac:
    feature_description[str(activity) + '_daily_usage'] = 0
    for i in range(plot_detail):
        feature_description[str(activity) + '_hourly_usage_' + str(i)] = 0
    feature_description[str(activity) + '_new_activity_for_this_device_for_user'] = 0
    feature_description[str(activity) + '_new_activity_for_this_device_for_role'] = 0
    feature_description[str(activity) + '_new_attribute_for_this_device_for_user'] = 0
    feature_description[str(activity) + '_new_attribute_for_this_device_for_role'] = 0
    feature_description[str(activity) + '_new_activity_for_any_device_for_user'] = 0
    feature_description[str(activity) + '_new_activity_for_any_device_for_role'] = 0
    feature_description[str(activity) + '_new_attribute_for_any_device_for_user'] = 0
    feature_description[str(activity) + '_new_attribute_for_any_device_for_role'] = 0
feature_list = list(feature_description)


filename_all_anomaly_results = os.getcwd() + '/static/output/' + scenario_name + '_pca_all_output.csv' 
filename_output_for_raw_features = os.getcwd() + '/static/output/' + scenario_name + '_all_features_' 
filename_output_for_alert_list = os.getcwd() + '/static/output/alert_list.json' 
filename_output_for_user_profiles = os.getcwd() + '/static/output/user_profiles/' 

filename_time = os.getcwd() + '/static/param/time.json'
filename_anomaly_weights = os.getcwd() + '/static/param/anomaly_weights.json' 

keep_going = True

first_run = True
training_data = True
#day_count_for_normal = 14 # this has been replaced with an actual date object
realtime = False



# Thresholds for when to report user - only output/report if greater than these
user_anomaly_threshold = 0.1
role_anomaly_threshold = 0.1
