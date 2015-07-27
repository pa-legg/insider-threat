#### 

### Profiler Version 2
# This version is to be updated so that we consider three different types of observations:
## - Today's observations
## - Previous observations (i.e., what we consider to be normal)
## - Suspicious observations

## We should only add to the user and role profiles if the anomaly score that comes back is acceptable


import global_values as gv
import numpy as np
import warnings


class Profiler:

    user_profile = {}
    role_profile = {}

    def __init__(self):
        pass

    def createNode(self, in_name):
        node = {}
        node['name'] = in_name
        node['usage'] = np.zeros(gv.plot_detail)
        node['mean'] = 0
        node['std'] = 0
        node['current_usage'] = []
        node['count'] = 0
        node['time_to_live'] = 30 # allow an activity 30 days before it is no longer considered normal
        node['last_observed'] = 0 # count since the day this activity was last observed
        node['children'] = {}
        node['first_new_user_observation'] = 0
        node['first_new_role_observation'] = 0
        node['this_new_user_observation'] = 0
        node['this_new_role_observation'] = 0
        return node

    def create_features(self, date, user_id, role_name):
        feature_description = {}
        # feature_description['current_devices_for_user'] = 0
        # feature_description['current_activities_for_user'] = 0
        # feature_description['current_attributes_for_user'] = 0
        # feature_description['current_devices_for_role'] = 0
        # feature_description['current_activities_for_role'] = 0
        # feature_description['current_attributes_for_role'] = 0

        feature_description['new_device_for_user'] = np.zeros([gv.plot_detail])
        feature_description['new_device_for_role'] = np.zeros([gv.plot_detail])
        # feature_description['new_activities_for_this_device_for_user'] = 0
        # feature_description['new_activities_for_this_device_for_role'] = 0
        # feature_description['new_attributes_for_this_device_for_user'] = 0
        # feature_description['new_attributes_for_this_device_for_role'] = 0
        # feature_description['new_activities_for_any_device_for_user'] = 0
        # feature_description['new_activities_for_any_device_for_role'] = 0
        # feature_description['new_attributes_for_any_device_for_user'] = 0
        # feature_description['new_attributes_for_any_device_for_role'] = 0

        feature_description['hourly_usage'] = np.zeros([gv.plot_detail])

        for activity in gv.ac:
            feature_description[str(activity) + '_daily_usage'] = 0
            feature_description[str(activity) + '_hourly_usage'] = np.zeros([gv.plot_detail])
            feature_description[str(activity) + '_new_activity_for_this_device_for_user'] = np.zeros([gv.plot_detail])
            feature_description[str(activity) + '_new_activity_for_this_device_for_role'] = np.zeros([gv.plot_detail])
            feature_description[str(activity) + '_new_attribute_for_this_device_for_user'] = np.zeros([gv.plot_detail])
            feature_description[str(activity) + '_new_attribute_for_this_device_for_role'] = np.zeros([gv.plot_detail])
            # feature_description[str(activity) + '_new_activity_for_any_device_for_user'] = np.zeros([gv.plot_detail])
            # feature_description[str(activity) + '_new_activity_for_any_device_for_role'] = np.zeros([gv.plot_detail])
            # feature_description[str(activity) + '_new_attribute_for_any_device_for_user'] = np.zeros([gv.plot_detail])
            # feature_description[str(activity) + '_new_attribute_for_any_device_for_role'] = np.zeros([gv.plot_detail])

        return feature_description


    def compare_record_to_current_profile(self, this_record, username, role_name):

        this_date = this_record['date']
        this_date_string = str(this_date.year) + '-' + str(this_date.month) + '-' + str(this_date.day)
        user_id = username
        activity = ''
        device = ''
        attribute_set = []

        if this_record.has_key('activity'):
            activity = this_record['activity']
            if 'Connect' in activity:
                activity = 'usb_insert'
            elif 'Disconnect' in activity:
                activity = 'usb_remove'
            if 'usb inserted' in activity:
                activity = 'usb_insert'
            elif 'Insert' in activity:
                activity = 'usb_insert'
            elif 'usb removed' in activity:
                activity = 'usb_remove'
            elif 'Remove' in activity:
                activity = 'usb_remove'
            elif 'login' in activity:
                activity = 'logon'
            elif 'Logon' in activity:
                activity = 'logon'
            elif 'logoff' in activity:
                activity = 'logoff'
            elif 'Logoff' in activity:
                activity = 'logoff'
            device = this_record['pc']
            attribute_set.append(device)

        if this_record.has_key('from'):
            activity = 'email'
            attribute_set = this_record['to'].split(";")
            device = 'na'

        if this_record.has_key('url'):
            activity = 'http'
            attribute_set.append(this_record['url'])
            device = 'na'

        if this_record.has_key('filename'):
            activity = 'file'
            attribute_set.append(this_record['filename'])
            device = 'na'

        # simply to switch to consistent terms
        

        #print this_date_string, user_id, activity, attribute_set, this_date.hour

        this_action = np.zeros([gv.plot_detail])
        k = this_date.hour
        this_action[k] = this_action[k] + 1

        ### USER COMPARISON
        if not self.user_profile.has_key(user_id):
            self.user_profile[user_id] = {}
            self.user_profile[user_id][gv.state[0]] = self.createNode(user_id)
            self.user_profile[user_id][gv.state[1]] = self.createNode(user_id)
            self.user_profile[user_id][gv.state[2]] = self.createNode(user_id)
            self.user_profile[user_id]['job_role'] = role_name

        if not self.user_profile[user_id][gv.state[0]].has_key('features'):
            self.user_profile[user_id][gv.state[0]]['features'] = self.create_features(this_date_string, user_id, role_name)

        if self.user_profile[user_id][gv.state[0]]['children'].has_key(device):
            if self.user_profile[user_id][gv.state[0]]['children'][device]['children'].has_key(activity):
                for attribute in attribute_set:
                    attribute_exists_in_profile = False
                    if self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'].has_key(attribute):
                        attribute_exists_in_profile = True
                    if not attribute_exists_in_profile:
                        self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'][attribute] = self.createNode(attribute)
                        self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_attribute_for_this_device_for_user'][k] += 1 
            else:
                self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity] = self.createNode(activity)
                self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_activity_for_this_device_for_user'][k] += 1
                for attribute in attribute_set:
                    self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'][attribute] = self.createNode(attribute)
                    self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_attribute_for_this_device_for_user'][k] += 1
        else:
            self.user_profile[user_id][gv.state[0]]['children'][device] = self.createNode(device)
            self.user_profile[user_id][gv.state[0]]['features']['new_device_for_user'][k] += 1
            self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity] = self.createNode(activity)
            self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_activity_for_this_device_for_user'][k] += 1
            for attribute in attribute_set:
                self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'][attribute] = self.createNode(attribute)
                self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_attribute_for_this_device_for_user'][k] += 1

        ### ROLE COMPARISON

        if not self.role_profile.has_key(role_name):
            self.role_profile[role_name] = {}
            self.role_profile[role_name][gv.state[0]] = self.createNode(role_name)
            self.role_profile[role_name][gv.state[1]] = self.createNode(role_name)

        if self.role_profile[role_name][gv.state[0]]['children'].has_key(device):
            if self.role_profile[role_name][gv.state[0]]['children'][device]['children'].has_key(activity):
                for attribute in attribute_set:
                    attribute_exists_in_profile = False
                    if self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'].has_key(attribute):
                        attribute_exists_in_profile = True
                    if attribute_exists_in_profile:
                        pass
                    else:
                        #print 'Create role attribute', attribute_set
                        self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'][attribute] = self.createNode(attribute)
                        self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_attribute_for_this_device_for_role'][k] += 1
            else:
                #print 'Create role activity/attribute', activity, attribute_set
                self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity] = self.createNode(activity)
                self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_activity_for_this_device_for_role'][k] += 1
                for attribute in attribute_set:
                    self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'][attribute] = self.createNode(attribute)
                    self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_attribute_for_this_device_for_role'][k] += 1
        else:
            #print 'Create role device/activity/attribute', device, activity, attribute_set
            self.role_profile[role_name][gv.state[0]]['children'][device] = self.createNode(device)
            self.user_profile[user_id][gv.state[0]]['features']['new_device_for_role'][k] += 1
            self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity] = self.createNode(activity)
            self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_activity_for_this_device_for_role'][k] += 1
            for attribute in attribute_set:
                self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'][attribute] = self.createNode(attribute)
                self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_new_attribute_for_this_device_for_role'][k] += 1
            
        ### --- POPULATE PROFILE WITH THIS ACTIVITY ---
        for attribute in attribute_set:
            self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'][attribute]['usage'] = np.array(self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'][attribute]['usage']) + this_action
            self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'][attribute]['count'] += 1
        self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['usage'] = np.array(self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['usage']) + this_action
        self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['count'] += 1
        self.user_profile[user_id][gv.state[0]]['children'][device]['usage'] = np.array(self.user_profile[user_id][gv.state[0]]['children'][device]['usage']) + this_action
        self.user_profile[user_id][gv.state[0]]['children'][device]['count'] += 1
        self.user_profile[user_id][gv.state[0]]['usage'] = np.array(self.user_profile[user_id][gv.state[0]]['usage']) + this_action
        self.user_profile[user_id][gv.state[0]]['count'] += 1

        self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_hourly_usage'] = self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['usage']
        self.user_profile[user_id][gv.state[0]]['features'][str(activity) + '_daily_usage'] = self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['count'] 
        self.user_profile[user_id][gv.state[0]]['features']['hourly_usage'] = self.user_profile[user_id][gv.state[0]]['usage']
        
        for attribute in attribute_set:
            self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'][attribute]['usage'] = np.array(self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'][attribute]['usage']) + this_action
            self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'][attribute]['count'] += 1
        self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['usage'] = np.array(self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['usage']) + this_action
        self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['count'] += 1
        self.role_profile[role_name][gv.state[0]]['children'][device]['usage'] = np.array(self.role_profile[role_name][gv.state[0]]['children'][device]['usage']) + this_action
        self.role_profile[role_name][gv.state[0]]['children'][device]['count'] += 1
        self.role_profile[role_name][gv.state[0]]['usage'] = np.array(self.role_profile[role_name][gv.state[0]]['usage']) + this_action
        self.role_profile[role_name][gv.state[0]]['count'] += 1

        #for f in self.user_profile[user_id][gv.state[0]]['features']:
        #    print f, self.user_profile[user_id][gv.state[0]]['features'][f]

        #raw_input("Press key...")

    def reset_observations(self):
        for user_id in self.user_profile:
            self.user_profile[user_id][gv.state[0]] = self.createNode(user_id)
            

    def append_nodes(self, previous_node, today_node):
        previous_node['usage'] = np.array(previous_node['usage']) + np.array(today_node['usage'])
        return previous_node

    def append_today_to_previous_observations(self):
        append_to_previous_observations = True
        for user_id in self.user_profile:
            if append_to_previous_observations:
                
                if not self.user_profile[user_id].has_key(gv.state[1]):
                    self.user_profile[user_id][gv.state[1]] = self.user_profile[user_id][gv.state[0]]
                else:
                    for device in self.user_profile[user_id][gv.state[0]]['children'].keys():
                        if not self.user_profile[user_id][gv.state[1]]['children'].has_key(device):
                            self.user_profile[user_id][gv.state[1]]['children'][device] = self.user_profile[user_id][gv.state[0]]['children'][device]
                        else:
                            for activity in self.user_profile[user_id][gv.state[0]]['children'][device]['children'].keys():
                                if not self.user_profile[user_id][gv.state[1]]['children'][device]['children'].has_key(activity):
                                    self.user_profile[user_id][gv.state[1]]['children'][device]['children'][activity] = self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]
                                else:
                                    for attribute in self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'].keys():
                                        if not self.user_profile[user_id][gv.state[1]]['children'][device]['children'][activity]['children'].has_key(attribute):
                                            self.user_profile[user_id][gv.state[1]]['children'][device]['children'][activity]['children'][attribute] = self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'][attribute]
                                        else:
                                            self.user_profile[user_id][gv.state[1]]['children'][device]['children'][activity]['children'][attribute] = self.append_nodes(self.user_profile[user_id][gv.state[1]]['children'][device]['children'][activity]['children'][attribute],self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity]['children'][attribute])
                                    self.user_profile[user_id][gv.state[1]]['children'][device]['children'][activity] = self.append_nodes(self.user_profile[user_id][gv.state[1]]['children'][device]['children'][activity],self.user_profile[user_id][gv.state[0]]['children'][device]['children'][activity])
                            self.user_profile[user_id][gv.state[1]]['children'][device] = self.append_nodes(self.user_profile[user_id][gv.state[1]]['children'][device],self.user_profile[user_id][gv.state[0]]['children'][device])
                    self.user_profile[user_id][gv.state[1]] = self.append_nodes(self.user_profile[user_id][gv.state[1]],self.user_profile[user_id][gv.state[0]])
                
                role_name = self.user_profile[user_id]['job_role']
                if not self.role_profile[role_name].has_key(gv.state[1]):
                    self.role_profile[role_name][gv.state[1]] = self.role_profile[role_name][gv.state[0]]
                else:
                    for device in self.role_profile[role_name][gv.state[0]]['children'].keys():
                        if not self.role_profile[role_name][gv.state[1]]['children'].has_key(device):
                            self.role_profile[role_name][gv.state[1]]['children'][device] = self.role_profile[role_name][gv.state[0]]['children'][device]
                        else:
                            for activity in self.role_profile[role_name][gv.state[0]]['children'][device]['children'].keys():
                                if not self.role_profile[role_name][gv.state[1]]['children'][device]['children'].has_key(activity):
                                    self.role_profile[role_name][gv.state[1]]['children'][device]['children'][activity] = self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]
                                else:
                                    for attribute in self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'].keys():
                                        if not self.role_profile[role_name][gv.state[1]]['children'][device]['children'][activity]['children'].has_key(attribute):
                                            self.role_profile[role_name][gv.state[1]]['children'][device]['children'][activity]['children'][attribute] = self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'][attribute]
                                        else:
                                            self.role_profile[role_name][gv.state[1]]['children'][device]['children'][activity]['children'][attribute] = self.append_nodes(self.role_profile[role_name][gv.state[1]]['children'][device]['children'][activity]['children'][attribute],self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity]['children'][attribute])
                                    self.role_profile[role_name][gv.state[1]]['children'][device]['children'][activity] = self.append_nodes(self.role_profile[role_name][gv.state[1]]['children'][device]['children'][activity],self.role_profile[role_name][gv.state[0]]['children'][device]['children'][activity])
                            self.role_profile[role_name][gv.state[1]]['children'][device] = self.append_nodes(self.role_profile[role_name][gv.state[1]]['children'][device],self.role_profile[role_name][gv.state[0]]['children'][device])
                    self.role_profile[role_name][gv.state[1]] = self.append_nodes(self.role_profile[role_name][gv.state[1]],self.role_profile[role_name][gv.state[0]])





