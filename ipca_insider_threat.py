from flask import Flask, render_template, request
from pymongo import Connection
#from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
import datetime
import numpy as np
from sklearn import preprocessing, decomposition
from sklearn import datasets
from profiler_v5 import Profiler
import global_values as gv
import collections

# GLOBAL VARIABLE DECLARATIONS
app = Flask(__name__)
data = {}
pca_2c = ''
MONGODB_HOST = 'localhost'#  '192.168.1.170' #'localhost'
MONGODB_PORT = 27017

ldap_user_tag = 'user'

normalize = False

DBS = ['scenario7', 'cmu_lite', 'cmu_r61']
DBS_NAME = DBS[1]
start_date = datetime.datetime(2010, 1, 1, 0, 0) #2010 for cmu, 2013 for oli
end_date = datetime.datetime(2011, 1, 1, 0, 0)
if DBS_NAME == 'cmu_lite':
    start_date = datetime.datetime(2010, 1, 1, 0, 0)
    end_date = datetime.datetime(2011, 1, 1, 0, 0)
    ldap_user_tag = 'user_id'
else:
    ldap_user_tag = 'user'
    start_date = datetime.datetime(2013, 1, 1, 0, 0) 
    end_date = datetime.datetime(2014, 1, 1, 0, 0)




number_of_days = 120
db_activities = ['logon', 'email', 'http', 'device', 'file'] # 'file' - not present in this dataset 
activities = ['logon', 'logoff', 'email', 'file', 'http', 'usb_insert']
types = ['_hourly_usage','_new_activity_for_this_device_for_role','_new_activity_for_this_device_for_user','_new_attribute_for_this_device_for_role','_new_attribute_for_this_device_for_user']
colour_detail = [[228,26,28], [55,126,184], [77,175,74], [152,78,163], [255,127,0], [255,255,51], [166,86,40], [247,129,191], [153,153,153]]

from_date = start_date
to_date = from_date + datetime.timedelta(days = number_of_days)
user_set = []
profiler = Profiler()

## FUNCTION DECLARATIONS IN ALPHABETICAL URL ORDER



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/clear_all_users")
def clear_all_users():
    global user_set
    print "clear_all_users"
    user_set = []
    return json.dumps(user_set)



@app.route("/get_anomaly_data_for_timeline")
def get_anomaly_data_for_timeline():
    global from_date, to_date, global_output
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    from_date = datetime.datetime.strptime(start_date, "%a, %d %b %Y %H:%M:%S GMT")
    current_date = datetime.datetime.strptime(start_date, "%a, %d %b %Y %H:%M:%S GMT")
    to_date = datetime.datetime.strptime(end_date, "%a, %d %b %Y %H:%M:%S GMT")
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    num_dimensions = 2
    print "Number of dimensions:", num_dimensions
    matrix_days = (to_date - from_date).days
    print from_date, to_date
    matrix_users = 100
    output = []
    print "Performing PCA on " + str(len(user_set)) + " users ..."
    matrix = []
    stats = []
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    from_date_string, to_date_string = get_date_strings(from_date, to_date)
    print from_date, to_date
    print from_date_string, to_date_string
    query = {'date': {"$gte":from_date, "$lt":to_date} }
    cursor = connection[DBS_NAME]['profile_out'].find(query).sort([('date', 1)])
    print query
    print "Start compiling matrix..."

    activities_types = []
    for a in activities:
        for t in types:
            activities_types.append(a + t)
    

    for c in cursor:
        #print c
        username = c['user']
        rolename = c['role']
        date = c['date']

        this_date = datetime.datetime.strftime(date, '%Y-%m-%d %H:%M:%S')
        print this_date
        date_val = (date - from_date).days
        row = []
        for at in activities_types:
            act_type = c[at]
            value = 0
            for item in range(24):
                if act_type.has_key(str(item)):
                    value = value + act_type[str(item)]
            row.append(value)

        matrix.append(row)
        stats.append([username,rolename,this_date,date_val,date])
    print "Finish matrix"
    output = []
    output2 = collections.OrderedDict({})
    np_matrix = np.array(matrix)



    if not num_dimensions or num_dimensions < 1 or num_dimensions > np_matrix.shape[1]:
        np_matrix = perform_pca(np_matrix, 2)
        for i in range(np_matrix.shape[0]):
            new_point = {}
            new_point['user'] = stats[i][0]
            new_point['role'] = stats[i][1]
            new_point['date'] = stats[i][2]
            new_point['date_val'] = stats[i][3]
            new_point['datetime'] = stats[i][4]
            new_point['x'] = np_matrix[i][0]
            new_point['y'] = np_matrix[i][1]
            new_point['_id'] = stats[i][2]
            new_point['count'] = abs(np.mean(np_matrix[i]))
            output.append(new_point)
            if output2.has_key(stats[i][2]):
                output2[stats[i][2]] = max(output2[stats[i][2]], new_point['count'])
            else:
                output2[stats[i][2]] = new_point['count']
    else:
        np_matrix = perform_pca(np_matrix, num_dimensions)
        for i in range(np_matrix.shape[0]):
            new_point = {}
            new_point['user'] = stats[i][0]
            new_point['role'] = stats[i][1]
            new_point['date'] = stats[i][2]
            new_point['date_val'] = stats[i][3]
            new_point['datetime'] = stats[i][4]
            new_point['x'] = stats[i][3]
            new_point['y'] = abs(np.mean(np_matrix[i]))
            new_point['_id'] = stats[i][2]
            new_point['count'] = abs(np.mean(np_matrix[i]))
            output.append(new_point)
            if output2.has_key(stats[i][2]):
                output2[stats[i][2]] = max(output2[stats[i][2]], new_point['count'])
            else:
                output2[stats[i][2]] = new_point['count']
    output3 = []
    for key in output2.keys():
        entry = {}
        entry['_id'] = key
        entry['count'] = output2[key]
        output3.append(entry)
    print "Complete: grab_features_perform_pca"
    global_output = output
    return json.dumps(output3)

def get_date_strings(from_date, to_date):
    if from_date.month < 10:
        month = '0' + str(from_date.month)
    else:
        month = str(from_date.month)
    if from_date.day < 10:
        day = '0' + str(from_date.day)
    else:
        day = str(from_date.day)

    from_date_string = str(from_date.year) + '-' + month + '-' + day

    if to_date.month < 10:
        month = '0' + str(to_date.month)
    else:
        month = str(to_date.month)
    if to_date.day < 10:
        day = '0' + str(to_date.day)
    else:
        day = str(to_date.day)
    to_date_string = str(to_date.year) + '-' + month + '-' + day
    return from_date_string, to_date_string

@app.route("/get_glyph_for_this_user_revised")
def get_glyph_for_this_user_revised():
    rolename = request.args.get('rolename')
    username = request.args.get('username')
    print "Starting get_glyph_for_this_user_revised..."

    connection = Connection(MONGODB_HOST, MONGODB_PORT)

    user_query_short = {ldap_user_tag: username }

    r_node = {}
    r_node['name'] = rolename
    r_node['userplot'] = []
    r_node['roleplot'] = []

    plot = {}
    user_plot = {}

    cursor_user = connection[DBS_NAME]['ldap'].find_one(user_query_short)
    print cursor_user
    email_address = cursor_user['email']

    query = {'user':username, 'date': {"$gte":from_date, "$lt":to_date} }
    #email_query = {'from':email_address, 'date': {"$gte":from_date_string, "$lt":to_date_string} }

    cursor = connection[DBS_NAME]['profile_out'].find(query)

    print query

    for c in cursor:
        print c
        
        for activity_ktu in activities:
            ktu = activity_ktu + '_hourly_usage'
            if c.has_key(ktu):
                for key in c[ktu].keys():
                    angle = int(key)
                    this_day = c['date'].split(" ")[0]
                    key_string = str(this_day) + "_" + str(angle)
                    if user_plot.has_key(key_string):
                        user_plot[key_string]['name'] = ktu
                        user_plot[key_string]['size'] = user_plot[key_string]['size'] + 1
                        user_plot[key_string]['colour'] = 'blue'
                        user_plot[key_string]['angle'] = angle
                        user_plot[key_string]['day'] = this_day
                        user_plot[key_string]['value'] = user_plot[key_string]['value'] + c[ktu][key]
                    else:
                        user_plot[key_string] = {}
                        user_plot[key_string]['name'] = ktu
                        user_plot[key_string]['size'] = 1
                        user_plot[key_string]['colour'] = 'blue'
                        user_plot[key_string]['angle'] = angle
                        user_plot[key_string]['day'] = this_day
                        user_plot[key_string]['value'] = c[ktu][key]

    for pp in user_plot:
        r_node['userplot'].append(user_plot[pp])

    print "Finished get_glyph_for_this_user_revised ..."

    connection.disconnect()
    return json.dumps(r_node)

@app.route("/get_detailed_glyph_for_this_user")
def get_detailed_glyph_for_this_user():
    rolename = request.args.get('rolename')
    details = request.args.get('details')
    print details

    if details == '':
        details = ['logon', 'device', 'http', 'file', 'email']
    else:
        details = details.split(",")
    print "Start Show all roles ..."
    print rolename
    print details

    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    roles = {}

    roles['name'] = rolename
    roles['children'] = []
    roles['max_radius'] = 0
    query = {'role':rolename}

    cursor_user = connection[DBS_NAME]['ldap'].find(query)

    

    for c_user in cursor_user:

        username = c_user[ldap_user_tag]
        email_address = c_user['email']

        u_node = {}
        u_node['name'] = username
        u_node['children'] = []

        query = {'user':username, 'date': {"$gte":from_date, "$lt":to_date} }
        email_query = {'user':username, 'date': {"$gte":from_date, "$lt":to_date} }
        if DBS_NAME == 'cmu_lite':
            email_query = {'from':email_address, 'date': {"$gte":from_date, "$lt":to_date} }

        

        for i in range(len(details)):
            cursor = connection[DBS_NAME][details[i]].find(query)
            if details[i] == 'email':
                cursor = connection[DBS_NAME][details[i]].find(email_query)
            for c in cursor:
                c['name'] = details[i]
                c['size'] = 2
                c['radius'] = (c['date'] - from_date).days
                if c['radius'] > roles['max_radius']:
                    roles['max_radius'] = c['radius']
                c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
                c['colour'] = colour_detail[i] 
                c['user'] = username
                c['role'] = rolename
                c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
                c.pop('_id', 0)
                c.pop('id',0)
                u_node['children'].append(c)
            roles['children'].append(u_node)


        # if 'device' in details:
        #     cursor = connection[DBS_NAME]['device'].find(query)
        #     for c in cursor:
        #         c['name'] = 'device'
        #         c['size'] = 2
        #         c['radius'] = (c['date'] - from_date).days
        #         if c['radius'] > roles['max_radius']:
        #             roles['max_radius'] = c['radius']
        #         c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
        #         c['colour'] = colour_detail[1] 
        #         c['user'] = username
        #         c['role'] = rolename
        #         c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
        #         c.pop('_id', 0)
        #         c.pop('id',0)
        #         u_node['children'].append(c)

        # cursor = connection[DBS_NAME]['email'].find(email_query)
        # for c in cursor:
        #     c['name'] = 'email'
        #     c['size'] = 2
        #     c['radius'] = (c['date'] - from_date).days
        #     if c['radius'] > roles['max_radius']:
        #         roles['max_radius'] = c['radius']
        #     c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
        #     c['colour'] = colour_detail[2] 
        #     c['user'] = username
        #     c['role'] = rolename
        #     c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
        #     c.pop('_id', 0)
        #     c.pop('id',0)
        #     u_node['children'].append(c)

        # cursor = connection[DBS_NAME]['http'].find(query)
        # for c in cursor:
        #     c['name'] = 'http'
        #     c['size'] = 2
        #     c['radius'] = (c['date'] - from_date).days
        #     if c['radius'] > roles['max_radius']:
        #         roles['max_radius'] = c['radius']
        #     c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
        #     c['colour'] = colour_detail[3] 
        #     c['user'] = username
        #     c['role'] = rolename
        #     c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
        #     c.pop('_id', 0)
        #     c.pop('id',0)
        #     u_node['children'].append(c)
        # roles['children'].append(u_node)

        # cursor = connection[DBS_NAME]['file'].find(query)
        # for c in cursor:
        #     c['name'] = 'file'
        #     c['size'] = 2
        #     c['radius'] = (c['date'] - from_date).days
        #     if c['radius'] > roles['max_radius']:
        #         roles['max_radius'] = c['radius']
        #     c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
        #     c['colour'] = colour_detail[4] 
        #     c['user'] = username
        #     c['role'] = rolename
        #     c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
        #     c.pop('_id', 0)
        #     c.pop('id',0)
        #     u_node['children'].append(c)
        # roles['children'].append(u_node)




        # if 'logon' in details:
        #     cursor = connection[DBS_NAME]['logon'].find(query)
        #     for c in cursor:
        #         c['name'] = 'logon'
        #         c['size'] = 2
        #         c['radius'] = (c['date'] - from_date).days
        #         if c['radius'] > roles['max_radius']:
        #             roles['max_radius'] = c['radius']
        #         c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
        #         c['colour'] = colour_detail[0] 
        #         c['user'] = username
        #         c['role'] = rolename
        #         c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
        #         c.pop('_id', 0)
        #         c.pop('id',0)
        #         u_node['children'].append(c)
        #     roles['children'].append(u_node)

        # if 'device' in details:
        #     cursor = connection[DBS_NAME]['device'].find(query)
        #     for c in cursor:
        #         c['name'] = 'device'
        #         c['size'] = 2
        #         c['radius'] = (c['date'] - from_date).days
        #         if c['radius'] > roles['max_radius']:
        #             roles['max_radius'] = c['radius']
        #         c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
        #         c['colour'] = colour_detail[1] 
        #         c['user'] = username
        #         c['role'] = rolename
        #         c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
        #         c.pop('_id', 0)
        #         c.pop('id',0)
        #         u_node['children'].append(c)
        #     roles['children'].append(u_node)

        # if 'email' in details:
        #     cursor = connection[DBS_NAME]['email'].find(email_query)
        #     for c in cursor:
        #         c['name'] = 'email'
        #         c['size'] = 2
        #         c['radius'] = (c['date'] - from_date).days
        #         if c['radius'] > roles['max_radius']:
        #             roles['max_radius'] = c['radius']
        #         c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
        #         c['colour'] = colour_detail[2] 
        #         c['user'] = username
        #         c['role'] = rolename
        #         c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
        #         c.pop('_id', 0)
        #         c.pop('id',0)
        #         u_node['children'].append(c)
        #     roles['children'].append(u_node)
            

        # if 'http' in details:
        #     cursor = connection[DBS_NAME]['http'].find(query)
        #     for c in cursor:
        #         c['name'] = 'http'
        #         c['size'] = 2
        #         c['radius'] = (c['date'] - from_date).days
        #         if c['radius'] > roles['max_radius']:
        #             roles['max_radius'] = c['radius']
        #         c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
        #         c['colour'] = colour_detail[3] 
        #         c['user'] = username
        #         c['role'] = rolename
        #         c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
        #         c.pop('_id', 0)
        #         c.pop('id',0)
        #         u_node['children'].append(c)
        #     roles['children'].append(u_node)

        # if 'file' in details:
        #     cursor = connection[DBS_NAME]['file'].find(query)
        #     for c in cursor:
        #         c['name'] = 'file'
        #         c['size'] = 2
        #         c['radius'] = (c['date'] - from_date).days
        #         if c['radius'] > roles['max_radius']:
        #             roles['max_radius'] = c['radius']
        #         c['angle'] = c['date'].hour + (float(c['date'].minute) / 60)
        #         c['colour'] = colour_detail[4] 
        #         c['user'] = username
        #         c['role'] = rolename
        #         c['date'] = str(c['date'].day) + "-" + str(c['date'].month) + "-" + str(c['date'].year) + "  " + str(c['date'].hour) + ":" + str(c['date'].minute)
        #         c.pop('_id', 0)
        #         c.pop('id',0)
        #         u_node['children'].append(c)
        #     roles['children'].append(u_node)

    print "Finished Show all roles ..."

    connection.disconnect()
    return json.dumps(roles)

    

@app.route("/get_new_anomalies_for_all_users_and_all_roles_revised")
def get_new_anomalies_for_all_users_and_all_roles_revised():
    print "/get_new_anomalies_for_all_users_and_all_roles_revised"
    final_data = []
    roles = {}
    users = {}
    print from_date, to_date
    for out in global_output:
        if out['datetime'] >= from_date and out['datetime'] < to_date:
            print out
            if roles.has_key(out['role']):
                roles[out['role']].append(out['user'])
            else:
                roles[out['role']] = [out['user']]

            if users.has_key(out['user']):
                users[out['user']] = users[out['user']] + out['count']
            else:
                users[out['user']] = out['count']
    for c_role in roles.keys():
        print c_role
        r_node = {}
        r_node['name'] = c_role
        r_node['count'] = 0
        r_node['selected'] = False
        r_node['children'] = []
        role_users = list(set(roles[c_role]))
        for c_user in role_users:
            print c_user
            u_node = {}
            u_node['name'] = c_user
            u_node['count'] = users[c_user]
            r_node['count'] = r_node['count'] + u_node['count']
            u_node['selected'] = False
            if {"user":c_user} in user_set:
                u_node['selected'] = True
                r_node['selected'] = True
            r_node['children'].append(u_node)
        r_node['count'] = r_node['count'] / len(role_users)
        final_data.append(r_node)
    print "Finished"
    return json.dumps(final_data)

@app.route("/inverse_pca")
def inverse_pca():
    pca_x = float(request.args.get('pca_x'))
    pca_y = float(request.args.get('pca_y'))
    point = np.array([[pca_x,pca_y]])
    result = pca_2c.inverse_transform(point)
    output = {}
    output['result'] = result.tolist()
    return json.dumps(output)

@app.route("/load_csv")
def load_csv():
    global data
    file_data = []
    #filename = 'data/cmu_lite_login_only.csv'
    filename = 'data/cmu_lite_all.csv'
    header = True
    data['target'] = []
    data['target_names'] = []
    data['data'] = []
    with open(filename, "r") as fd:
        for row in fd:
            d = row.split(',')
            if header:
                data['headers'] = d
                data['feature_names'] = d[3:]
                header = False
            else:
                data['target'].append(d[2])
                data['target_names'].append(d[2])
                data['data'].append(d[3:])
            file_data.append(d)
    limit = 1000
    data['data'] = data['data'][0:limit]
    data['target'] = data['target'][0:limit]

    data['data'] = np.array(data['data'])
    data['target_names'] = list(set(data['target_names']))
    for i in range(len(data['target'])):
        #print i
        #print data['target'][i]
        #print data['target_names'].index(data['target'][i])
        data['target'][i] = data['target_names'].index(data['target'][i])
    #data['target'] = np.array(data['target'])
    return json.dumps({"load":"done"})
    
@app.route("/load_example")
def load_example():
    global data
    data = datasets.load_iris()
    data['target_names'] = data['target_names'].tolist()
    data['target'] = data['target'].tolist()
    return json.dumps({"load":"done"})

def perform_pca(data, number_of_dimensions):
    X = data
    if normalize:
        X = preprocessing.normalize(X, axis=0, norm='l1')
    pca = decomposition.PCA(n_components = number_of_dimensions)
    pca_model = pca.fit(X)
    X_reduced = pca_model.transform(X)
    return X_reduced

@app.route("/prepare_data")
def prepare_data():
    global pca_2c, pca_model
    output = {}

    # remove normalization so that we can do the inverse PCA in interactive mode
    X = data['data'] #preprocessing.normalize(data['data'], axis=0, norm='l1')
    print X
    print X.shape


    pca = decomposition.PCA()
    pca_2c = decomposition.PCA(n_components=2)
    pca_2c.fit(X)
    X_reduced = pca.fit_transform(X)
    
    output['pca'] = X_reduced.tolist()
    output['data'] = data['data'].tolist()

    output['axes'] = data['feature_names']
    output['target'] = data['target']
    output['target_names'] = data['target_names']
    return json.dumps(output)

@app.route("/prepare_real_data")
def prepare_real_data():
    global data, pca_2c, pca_model
    selected_features = request.args.get('selected_features')
    print "selected_features: ", selected_features
    if selected_features == '':
        selected_features = []
    else:
        selected_features = selected_features.split(",")
    print "selected_features: ", selected_features

    data = {}
    data['target'] = []
    data['target_names'] = []
    data['data'] = []
    data['axes'] = []
    data['detail'] = []

    num_dimensions = 2 # int(request.args.get('num_dimensions'))

    if len(user_set) > 0:
        full_matrix = []
        connection = Connection(MONGODB_HOST, MONGODB_PORT)
        query_or = {'$and' : [ {'$or':user_set}, {'date': {"$gte":from_date, "$lt":to_date} } ] }
        print query_or
        cursor = connection[DBS_NAME]['profile_out'].find(query_or).sort([('date', 1)])

        if len(selected_features) > 0:
            for a in activities:
                for t in types:
                    feat = a+t
                    if feat in selected_features:
                        data['axes'].append(feat)
        else:
            # use all features
            for a in activities:
                for t in types:
                    data['axes'].append(a + t)

        
        print "Start compiling matrix..."
        for c in cursor:
            #print c
            username = c['user']
            rolename = c['role']
            date = c['date']
            date_val = (date - from_date).days

            full_row = []
            full_row.append(str(date))
            full_row.append(username)
            full_row.append(rolename)

            if len(selected_features) > 0:
                for a in activities:
                    for t in types:
                        feat = a+t
                        if feat in selected_features:
                            act_type = c[feat]
                            value = 0
                            for item in range(24):
                                if act_type.has_key(str(item)):
                                    value = value + act_type[str(item)]
                            full_row.append(value)
            else:
                for a in activities:
                    for t in types:
                        act_type = c[a + t]
                        value = 0
                        for item in range(24):
                            if act_type.has_key(str(item)):
                                value = value + act_type[str(item)]
                        full_row.append(value)




            data['data'].append(full_row[3:])
            data['target'].append(rolename)
            data['target_names'].append(rolename)
            data['detail'].append(full_row[0:2])

        data['target_names'] = list(set(data['target_names']))

        for i in range(len(data['target'])):
            data['target'][i] = data['target_names'].index(data['target'][i])


        print "Finish matrix"

        X = np.array(data['data'])
        if normalize:
            X = preprocessing.normalize(X, axis=0, norm='l1')
        pca = decomposition.PCA()
        pca_2c = decomposition.PCA(n_components=2)
        pca_2c.fit(X)
        X_reduced = pca.fit_transform(X)
        data['pca'] = X_reduced.tolist()

    return json.dumps(data)



# This is a function for performing user profiling (like we do for detection tool)
# Useful to have this integrated for when dealing with new db (rather than relying on the old code)
@app.route("/profiler")
def perform_profiler():
    global from_date, to_date

    print "Performing profiling... this may take some time... "
    data = []
    from_date = start_date
    current_date = start_date
    current_date_plus_one = current_date + datetime.timedelta(days=1)
    to_date = end_date

    connection = Connection(MONGODB_HOST, MONGODB_PORT)

    while current_date < to_date:
        print current_date
        current_date_plus_one = current_date + datetime.timedelta(days=1)
        query = {'date': {"$gte":current_date, "$lt":current_date_plus_one} }
        print query
        for a in db_activities:
            print a
            cursor = connection[DBS_NAME][a].find(query)
            for record in cursor:
                #print record
                username = ''
                if a == 'email':
                    #username = record['user']
                    username = connection[DBS_NAME]['ldap'].find_one({"email":record['from']})['user_id']
                else:
                    username = record['user']
                role = connection[DBS_NAME]['ldap'].find_one({"user_id":username})['role'] #cmu_lite
                #role = connection[DBS_NAME]['ldap'].find_one({"user":username})['role']
                profiler.compare_record_to_current_profile(record, username, role)
        # Compute features here and save to mongo
        save_raw_features_to_mongo(current_date, profiler.user_profile)
        # Then set configuration ready for next day
        profiler.append_today_to_previous_observations()
        profiler.reset_observations()
        current_date = current_date_plus_one
    return json.dumps({"profiler":"done"})

def save_raw_features_to_mongo(current_date, user_profile):
    output2_json = []
    connection = Connection(MONGODB_HOST, MONGODB_PORT)

    db_name = 'profile_out'

    for u in user_profile:
        new_dict = {}
        new_dict['user'] = u
        new_dict['role'] = user_profile[u]['job_role']
        new_dict['date'] = str(current_date)

        key_list = ['hourly_usage', 'new_device_for_user', 'new_device_for_role']
        for f in key_list:
            new_dict[f] = {}
            value = 0
            if user_profile[u][gv.state[0]].has_key('features'):
                this_list = user_profile[u][gv.state[0]]['features'][f]
                for i in range(len(this_list)):
                    if this_list[i] > 0:
                        new_dict[f][str(i)] = this_list[i] #.append({str(i):this_list[i]})
                        value = value + this_list[i]
            new_dict['value_' + f] = value

        for activity in gv.ac:
            #new_dict[activity] = {}
            key_list = [str(activity) + '_hourly_usage', str(activity) + '_new_activity_for_this_device_for_user', str(activity) + '_new_activity_for_this_device_for_role', str(activity) + '_new_attribute_for_this_device_for_user', str(activity) + '_new_attribute_for_this_device_for_role']
            
            for f in key_list:
                value = 0
                ff = f #f[len(activity)+1:]
                new_dict[ff] = {}
                if user_profile[u][gv.state[0]].has_key('features'):
                    this_list = user_profile[u][gv.state[0]]['features'][f]
                    for i in range(len(this_list)):
                        if this_list[i] > 0:
                            new_dict[ff][str(i)] = this_list[i] #.append({str(i):this_list[i]})
                            value = value + this_list[i]
                new_dict['value_' + f] = value

        output2_json.append(new_dict)
        result = connection[DBS_NAME][db_name].insert(new_dict)

@app.route("/set_date_range")
def set_date_range():
    global from_date, to_date
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    from_date = datetime.datetime.strptime(start_date, "%a, %d %b %Y %H:%M:%S GMT")
    to_date = datetime.datetime.strptime(end_date, "%a, %d %b %Y %H:%M:%S GMT")

    print start_date
    print end_date
    return json.dumps({"update":"true", "data": [start_date, end_date]})

@app.route("/set_normalize_pca")
def set_normalize_pca():
    global normalize
    normalize = not normalize
    return json.dumps({"update":"true", "data": normalize})

@app.route("/set_selected_features")
def set_selected_features():
    global activities, types
    activities = request.args.get('activities').split(",")

    types = request.args.get('types').split(",")

    for a in activities:
        for t in types:
            print a + t


    return json.dumps({"update":"true", "data": activities})

@app.route("/show_features")
def show_features():
    #data['data']
    #data['feature_names']
    #data['target']
    #data['target_names']
    
    return json.dumps(output)

@app.route("/update_server_on_role_selection")
def update_server_on_role_selection():
    global user_set
    rolename = request.args.get('rolename')
    add = request.args.get('add') == 'true'
    print "add: " , add

    query = {'role':rolename}
    connection = Connection(MONGODB_HOST, MONGODB_PORT)
    cursor_user = connection[DBS_NAME]['ldap'].find(query)
    for c_user in cursor_user:
        if add:
            if not {"user":c_user[ldap_user_tag]} in user_set:
                user_set.append({"user":c_user[ldap_user_tag]})
        else:
            if {"user":c_user[ldap_user_tag]} in user_set:
                user_set.pop(user_set.index({"user":c_user[ldap_user_tag]}))
    return json.dumps({"update":"true", "data": user_set})

@app.route("/update_server_on_user_selection")
def update_server_on_user_selection():
    global user_set
    username = request.args.get('username')
    add = request.args.get('add') == 'true'
    print "add: " , add

    #user_set.remove({"user":username})
    if add:
        if not {"user":username} in user_set:
            user_set.append({"user":username})
    else:
        if {"user":username} in user_set:
            user_set.pop(user_set.index({"user":username}))
    return json.dumps({"update":"true", "data": user_set})


    






if __name__ == "__main__":
    #load_csv()
    #load_example()
    app.run(host='localhost',port=7234,debug=True)
