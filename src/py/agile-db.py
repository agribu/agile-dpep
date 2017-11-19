#!/usr/bin/python3
# Documentation available: https://github.com/agribu/agile-db/wiki/AGILE-Database-entities
import os, re, json, argparse
from utils import mysqlc

# Main configuration file
main_conf = None
# Path to agile_conf.json
agile_conf = None
# Path to db_conf.json
db_conf = None
# Path to agile-sdk-handler
agile = None

# Helper: counter for database id creation
db_ctr = 0
# Helper: counter for table id creation
tab_ctr = 0
# Helper: counter for column id creation
col_ctr = 0

# ##################################### #
#  main function                        #
# ##################################### #
def main():
    global main_conf, agile_conf, db_conf, agile
    parser = argparse.ArgumentParser(description='This python script includes functions to translate a database with its tables and columns into AGILE entities')
    parser.add_argument('-c','--config', help='Config file',required=True)
    parser.add_argument('--createDatabase', help='Creates a database entity based on a provided configuration', action='store_true', required=False)
    parser.add_argument('--createTables', help='Creates table entities from the configured database', action='store_true', required=False)
    parser.add_argument('--createColumns', help='Creates column entities from the configured database', action='store_true', required=False)
    parser.add_argument('--deleteAll', help='Deletes all entities of a particular type', required=False)
    parser.add_argument('--dbInit', help='Creates the database, and all tables and column entites', action='store_true', required=False)
    parser.add_argument('--dbReset', help='Deletes the database, and all tables and column entites', action='store_true', required=False)
    args = parser.parse_args()

    if args.config:
        with open(args.config) as json_data_file:
            main_conf = json.load(json_data_file)

        agile_conf = main_conf["agile_conf"]
        db_conf = main_conf["db_conf"]
        agile = main_conf["agile-sdk-handler"]

        mysqlc.readJSONFile(db_conf)
        mysqlc.connect()

        if args.createDatabase:
            createDatabase()
        if args.createTables:
            createTables()
        if args.createColumns:
            createAllColumns()
        if args.deleteAll:
            typename = args.deleteAll
            deleteAll(typename)
        if args.dbInit:
            dbInit()
        if args.dbReset:
            dbReset()

        mysqlc.terminate()

# ##################################### #
#  helper functions                     #
# ##################################### #
def run(cmd):
    nodejs = "/usr/bin/nodejs "
    return os.popen(nodejs + cmd).read()

def extractIDs(s):
    identifiers = []
    result = re.findall(r'\"id\"\:\s\".+', s)
    for eid in result:
        identifiers.append(eid.split('"id": "')[1].split('",')[0])
    return identifiers

# ##################################### #
#  database functions                   #
# ##################################### #
def createDatabase():
    global db_ctr
    db_ctr += 1
    db_id = mysqlc.config["name"] + "!@!db"
    debug = run(agile
        + " --conf " + agile_conf
        + " --createEntity"
        + " --id " + db_id
        + " --type " + "'db'"
        + " --name " + mysqlc.config["name"])
    print(debug) # debug output

    for key, value in mysqlc.config.items():
        if key not in "name":
            debug = run(agile
                + " --conf " + agile_conf
                + " --setEntityAttribute"
                + " --id " + db_id
                + " --type " + "'db'"
                + " --attr " + key
                + " --value " + value)
        print(debug) # debug output

def createTables():
    global tab_ctr
    tables = mysqlc.getTables()
    for table in tables:
        tab_ctr += 1
        db_tab_id = str(tab_ctr) + "-" + mysqlc.config["name"] + "!@!db"
        debug = run(agile
            + " --conf " + agile_conf
            + " --createDatabaseColumn"
            + " --id " + db_tab_id
            + " --type " + "'db-table'"
            + " --database " + mysqlc.config["name"]
            + " --table " + table)
        print(debug)

def createColumns(table, index, c):
    columns = mysqlc.getColumns(table)
    debug = table + " : " + ','.join(columns)

    # for c in columns:
    debug = run(agile
        + " --conf " + agile_conf
        + " --createDatabaseColumn"
        + " --id " + index + "-" + mysqlc.config["name"] + "!@!db"
        + " --type " + "'db-column'"
        + " --database " + mysqlc.config["name"]
        + " --table " + table
        + " --column " + c)
    print(debug)

def createAllColumns():
    global tab_ctr, col_ctr
    tab_ctr = 0
    col_ctr = 0
    for t in mysqlc.getTables():
        tab_ctr += 1
        for c in mysqlc.getColumns(t):
            col_ctr += 1
            createColumns(t, str(tab_ctr) + "." + str(col_ctr), c)
        col_ctr = 0

def deleteAll(typename):
    result = run(agile
        + " --conf " + agile_conf
        + " --getEntityByType"
        + " --type " + typename)
    for identifier in extractIDs(result):
        debug = run(agile
            + " --conf " + agile_conf
            + " --deleteEntity"
            + " --id " + identifier
            + " --type " + typename)
        print(debug + " - " + identifier)

# ##################################### #
#  quick functions                      #
# ##################################### #
def dbInit():
    createDatabase()
    createTables()
    createAllColumns()

def dbReset():
    deleteAll("'db'")
    deleteAll("'db-table'")
    deleteAll("'db-column'")

# ##################################### #
#  start                                #
# ##################################### #
if __name__ == "__main__":
   main()
