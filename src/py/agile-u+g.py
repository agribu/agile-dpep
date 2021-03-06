#!/usr/bin/python3
# /*******************************************************************************
#  * Copyright (c) Benjamin Schuermann.
#  * All rights reserved. This program and the accompanying materials
#  * are made available under the terms of the Eclipse Public License v1.0
#  * which accompanies this distribution, and is available at
#  * http://www.eclipse.org/legal/epl-v10.html
#  *
#  * Contributors:
#  *     Benjamin Schuermann
#  ******************************************************************************/
# Documentation available: https://github.com/agribu/agile-db/wiki/agile%E2%80%90u%CB%96g.py
import os, re, json, argparse
from utils import mysqlc
from utils import helpers

# Main configuration file
main_conf = None
# Path to agile_conf.json
agile_conf = None
# Path to example_groups.json
example_groups = None
# Path to example_users.json
example_users = None
# Path to agile-sdk-handler
agile = None

# ##################################### #
#  main function                        #
# ##################################### #
def main():
    global main_conf, agile_conf, agile, example_users, example_groups
    parser = argparse.ArgumentParser(description='This python script includes functions to create AGILE user and group entities')
    parser.add_argument('--conf', help='Config file',required=True)
    parser.add_argument('--createExampleUsers', help='Creates some example users for testing the emergency policy scenario', action='store_true', required=False)
    parser.add_argument('--deleteExampleUsers', help='Deletes all example users', action='store_true', required=False)
    parser.add_argument('--createExampleGroups', help='Creates some example groups for testing the emergency policy scenario', action='store_true', required=False)
    parser.add_argument('--deleteExampleGroups', help='Deletes all example groups', action='store_true', required=False)
    parser.add_argument('--createMappings', help='Maps example users to example groups', action='store_true', required=False)
    parser.add_argument('--deleteMappings', help='Deletes all mapping of example users to example groups', action='store_true', required=False)
    parser.add_argument('--createExamples', help='Creates all example users, example groups and mapping between them', action='store_true', required=False)
    parser.add_argument('--deleteExamples', help='Deletes all example users, example groups and mapping between them', action='store_true', required=False)
    args = parser.parse_args()

    if args.conf:
        with open(args.conf) as json_data_file:
            main_conf = json.load(json_data_file)

        helpers.initialize(args.conf)

        agile_conf = main_conf["agile_conf"]
        db_conf = main_conf["db_conf"]
        agile = main_conf["agile-sdk-handler"]
        example_users = main_conf["example_users"]
        example_groups = main_conf["example_groups"]

    if args.createExampleUsers:
        createExampleUsers()
    if args.deleteExampleUsers:
        deleteExampleUsers()
    if args.createExampleGroups:
        createExampleGroups()
    if args.deleteExampleGroups:
        deleteExampleGroups()
    if args.createMappings:
        createMappings()
    if args.deleteMappings:
        deleteMappings()
    if args.createExamples:
        createExamples()
    if args.deleteExamples:
        deleteExamples()

# ##################################### #
#  AGILE user functions                 #
# ##################################### #
def addUser(username, authtype, role, password):
    debug = helpers.run(agile
        + " --conf " + agile_conf
        + " --createUser"
        + " --username " + username
        + " --authtype " + authtype
        + " --role " + role
        + " --password " + password)
    print(debug)
    return debug

def getUser(username, authtype):
    debug = helpers.run(agile
        + " --conf " + agile_conf
        + " --getUser"
        + " --username " + username
        + " --authtype " + authtype)
    print(debug)
    return debug

def deleteUser(username, authtype):
    debug = helpers.run(agile
        + " --conf " + agile_conf
        + " --deleteUser"
        + " --username " + username
        + " --authtype " + authtype)
    print(debug)
    return debug

# ##################################### #
#  AGILE group functions                #
# ##################################### #
def createGroup(name):
    debug = helpers.run(agile
        + " --conf " + agile_conf
        + " --createGroup"
        + " --name " + name)
    print(debug)
    return debug

def deleteGroup(ownerid, name):
    debug = helpers.run(agile
        + " --conf " + agile_conf
        + " --deleteGroup"
        + " --ownerid " + ownerid
        + " --name " + name)
    print(debug)
    return debug

def groupAddEntity(ownerid, group, entityid, entitytype):
    debug = helpers.run(agile
        + " --conf " + agile_conf
        + " --groupAddEntity"
        + " --ownerid " + ownerid
        + " --group " + group
        + " --entityid " + entityid
        + " --type " + entitytype)
    print(debug)
    return debug

def groupRemoveEntity(ownerid, group, entityid, entitytype):
    debug = helpers.run(agile
        + " --conf " + agile_conf
        + " --groupRemoveEntity"
        + " --ownerid " + ownerid
        + " --group " + group
        + " --entityid " + entityid
        + " --type " + entitytype)
    print(debug)
    return debug

# ##################################### #
#  example_users functions              #
# ##################################### #
def createExampleUsers():
    global example_users
    users = None
    with open(example_users) as json_data_file:
        users = json.load(json_data_file)

    for item in users.keys():
        for x in users[item]:
            username = x["user_name"]
            authtype = x["auth_type"]
            role = x["role"]
            password = x["password"]
            addUser(username, authtype, role, password);

def deleteExampleUsers():
    global example_users
    users = None
    with open(example_users) as json_data_file:
        users = json.load(json_data_file)

    for item in users.keys():
        for x in users[item]:
            username = x["user_name"]
            authtype = x["auth_type"]
            deleteUser(username, authtype);

# ##################################### #
#  example_groups functions             #
# ##################################### #
def createExampleGroups():
    global example_groups
    groups = None
    with open(example_groups) as json_data_file:
        groups = json.load(json_data_file)

    for name in groups:
        createGroup(name)

def deleteExampleGroups():
    global example_groups
    groups = None
    with open(example_groups) as json_data_file:
        groups = json.load(json_data_file)

    for name in groups:
        ownerid = helpers.getCurrentUserInfo()["id"]
        deleteGroup(ownerid, name)

# ##################################### #
#  example_mapping functions            #
# ##################################### #
def createMappings():
    global example_groups, example_users
    users = None
    groups = None
    with open(example_groups) as json_data_file:
        groups = json.load(json_data_file)
    with open(example_users) as json_data_file:
        users = json.load(json_data_file)

    for item in users.keys():
            for group in groups:
                if (item == group):
                    for x in users[item]:
                        user = str(getUser(x["user_name"], x["auth_type"]))
                        print(user)
                        entityid = helpers.getJSON(user)["id"]
                        ownerid = helpers.getCurrentUserInfo()["id"]
                        groupAddEntity(ownerid, group, entityid, 'user')

def deleteMappings():
    global example_groups, example_users
    users = None
    groups = None
    with open(example_groups) as json_data_file:
        groups = json.load(json_data_file)
    with open(example_users) as json_data_file:
        users = json.load(json_data_file)

    for item in users.keys():
            for group in groups:
                if (item == group):
                    for x in users[item]:
                        user = str(getUser(x["user_name"], x["auth_type"]))
                        entityid = helpers.getJSON(user)["id"]
                        ownerid = helpers.getCurrentUserInfo()["id"]
                        groupRemoveEntity(ownerid, group, entityid, 'user')

# ##################################### #
#  quick functions                      #
# ##################################### #
def createExamples():
    createExampleUsers()
    createExampleGroups()
    createMappings()

def deleteExamples():
    deleteExampleUsers()
    deleteExampleGroups()

# ##################################### #
#  start                                #
# ##################################### #
if __name__ == "__main__":
   main()
