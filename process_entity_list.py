#!/usr/bin/python -tt

import re
import os
import requests


#
# Read the list of entities
# Put them in a file :-)
#
# Content starts with: "public enum EntityType\n
# {"
# Content is in the format:
#     ACTION_PLAN(ActionPlan.class, (e, rb) -> rb.buildActionPlanLink(e)), //
#     ALARM(MetricAlarm.class, (final MetricAlarm< ? blah blah
#         if (Abst
# Content ends with:
#    "private interface RESTLinkBuilder<T>"
#
# New tracer.properties is in:
# /Users/maryjane/platform/api/src/main/resources/tracer
#
# List of entities is in:
# ./api/src/main/java/com/abiquo/api/tracer/entity/EntityType.java
# 
# Note that previous script used a single string for the file
#

def process():
    entity_list_code_dir = "../platform/api/src/main/java/com" + \
        "/abiquo/api/tracer/entity/EntityType.java"
    entity_code_file = "EntityType.java"

    with open(os.path.join(
            entity_list_code_dir,
            entity_code_file), "r") as efile:
        edata = efile.read().replace('\n', '')

    top_split = "public enum EntityType\n{"
    bottom_split = "private interface RESTLinkBuilder"
    top_erecords = (re.split(top_split, edata))[1]
    e_raw_records = (re.split(bottom_split, top_erecords))[0]

    # we want $1 from this findall... it's a list of matches with [$0, $1]?
    e_records = (re.findall("\s{4}([A-Z,_])*?\(", e_raw_records))

    for er in e_records:
        print ("er: %s", er)

    # e_records = re.split(RS, edata)
    # entity_list = "entity_list_" + td + ".txt"
    # entity_action_list = "entity_action_list_" + td + ".txt"

    # the output file from this script is used as an input file
    # for another script
    # input_subdir = "input_files"


def do_api_request(apiAuth, apiIP, apiUrl, apiAccept):
        print "API URL: %s" % apiUrl
        apiHeaders = {}
        apiHeaders['Accept'] = apiAccept
        apiHeaders['Authorization'] = apiAuth
        r = requests.get(apiUrl, headers=apiHeaders, verify=False)
        r_data = r.json()
        return r_data


def get_api_privs(apiAuth, apiIP):
    # Get role data from the API of a fresh Abiquo
    # First get roles and IDs, then get privileges of each role
    roles_data = {}
    # get all base role names and ID numbers
    apiUrl = 'https://' + apiIP + '/api/admin/roles/'
    apiAccept = 'application/vnd.abiquo.roles+json'
    default_roles_response = do_api_request(
        apiAuth,
        apiIP,
        apiUrl,
        apiAccept)
    default_roles_list = ["CLOUD_ADMIN",
                          "ENTERPRISE_ADMIN",
                          "USER",
                          "OUTBOUND_API",
                          "ENTERPRISE_VIEWER"]
    default_roles = {}
    default_roles_list = default_roles_response['collection']
    # create a dictionary with the roles and their IDs
    for dr in default_roles_list:
        default_roles[dr['name']] = dr['id']
    # run through the dictionary and get the privileges for each role
    for drname, drid in default_roles.iteritems():
        apiUrl = 'https://' + apiIP + '/api/admin/roles/' \
            + str(drid) + '/action/privileges'
        print "API URL: %s" % apiUrl
        apiAccept = 'application/vnd.abiquo.privileges+json;version=4.6'

        default_privileges_response = do_api_request(
            apiAuth,
            apiIP,
            apiUrl,
            apiAccept)
    # create a list like the sql list
        default_privileges_list = []
        default_privileges_list = default_privileges_response['collection']
        for rp in default_privileges_list:
            pname = rp['name']
            if pname in roles_data:
                roles_data[pname].append(drname)
            else:
                roles_data[pname] = [drname]
            for rrr in roles_data:
                print "rrr: %s" % rrr
    return roles_data


def main():
    td = "2019-10-21"

    entity_list_code_dir = "../platform/api/src/main/java/com" + \
        "/abiquo/api/tracer/entity"
    entity_code_file = "EntityType.java"

    with open(os.path.join(
            entity_list_code_dir,
            entity_code_file), "r") as efile:
        edata = efile.read().replace('\n', '')

    top_split = "public enum EntityType"
    bottom_split = "private interface RESTLinkBuilder"
    top_erecords = (re.split(top_split, edata))[1]
    e_raw_records = (re.split(bottom_split, top_erecords))[0]

    # we want $1 from this findall... it's a list of matches with [$0, $1]?
    e_records = (re.findall(
        "(\s{4}|\)\,\s)([A-Z,_]+?)(\(|\,)", e_raw_records))

    for er in e_records:
        eri = er[1]
        print ("er: %s" % eri)

    entity_list = "entity_list_" + td + ".txt"

    # the output file from this script is used as an input file
    # for another script
    input_subdir = "input_files"
    with open(os.path.join(input_subdir, entity_list), 'w') as g:
        for ero in e_records:
            era = ero[1]
            EntityNameOut = era + "\n"
            g.write(EntityNameOut)

#     # use API to get default roles and privileges
#     # the format is roles_data[priv] = [role1, role2, role3]
#     #   apiAuth = input("Enter API authorization, e.g. Basic XXXX: ")
#     apiAuth = "Basic YWRtaW46eGFiaXF1bw=="
#     apiIP = raw_input("Enter API address, e.g. api.abiquo.com: ")
#     #   apiroles = get_api_privs(apiAuth,apiIP)

#     FS = "new KEYS"
#     RS = "public static final class|public static final Action|Master"
#     NRSave = 0
#     EntityName = ""
#     ActionName = ""
#     startout = {}
#     entityout = {}
#     endout = {}
#     entityheader = {}
#     entity_space_action = {}
#     entity_underscore_actions = {}
#     entity_for_users = {}
#     event_list_with_privileges = {}

#     td = "2019-07-24"

#     roles_data = {}
#     roles_data = get_api_privs(apiAuth, apiIP)

#     git_events_security_dir = "../platform/api/src/main/resources/events"
#     events_security_privileges_file = "events-security.properties"
#     events_security_file = [es.strip() for es in open(os.path.join(
#         git_events_security_dir,
#         events_security_privileges_file))]

#     entity_action_list_git_dir = "../platform/model/event-model-transport" + \
#         "/src/main/java/com/abiquo/event/model/enumerations"
#     entity_action_git_file = "EntityAction.java"

#     entity_list = "entity_list_" + td + ".txt"
#     entity_action_list = "entity_action_list_" + td + ".txt"

#     user_entity_action_list = "entity_action_list_user_" + td + ".txt"
#     ent_admin_entity_action_list = "entity_action_list_ent_admin_" + \
#         td + ".txt"

#     user_entity_list = "entity_list_user_" + td + ".txt"
#     ent_admin_entity_list = "entity_list_ent_admin_" + td + ".txt"

#     input_subdir = "input_files"
#     out_subdir = "output_files"
#     wiki_entity_action_privileges_file = "wiki_entity_action_privileges_" + \
#         td + ".txt"

#     # Events security file in format:
#     # APPLIB_MANAGE_CATEGORIES =
#     # CATEGORY.CREATE, CATEGORY.DELETE, CATEGORY.MODIFY
#     # make a list of entities for printing
#     entity_entity = {}
#     entity_action = {}

#     user_out = []
#     ent_admin_out = []
#     ent_admin_entity_out = []
#     user_entity_out = []

#     for esi in events_security_file:
#         #       print ("esi: ",esi)
#         esSplit = esi.split("=")
#         es_privilege = esSplit[0]
#         es_privilege = es_privilege.strip()
#         es_event_list = esSplit[1]
#         elSplit = es_event_list.split(",")
#         for els in elSplit:
#             elsa = els.strip()
# #           write the entity_action to a file
#             entity_action[elsa] = elsa
# #           substitute the dot for an underscore
#             event_list_event = re.sub("\.", "_", els)
#             event_list_event = event_list_event.strip()

#             # Replace with setdefault when have time?
#             if event_list_event not in event_list_with_privileges:
#                 event_list_with_privileges[event_list_event] = [es_privilege]
#             else:
#                 if es_privilege not in \
#                         event_list_with_privileges[event_list_event]:
#                     event_list_with_privileges[event_list_event].append(
#                         es_privilege)

#     with open(os.path.join(
#             entity_action_list_git_dir,
#             entity_action_git_file), "r") as eafile:
#         eadata = eafile.read().replace('\n', '')

#     ea_records = re.split(RS, eadata)

#     for NR, ear in enumerate(ea_records):
#         #       print ("NR: ", NR)
#         NRSave = NR
#         ea_fields = re.split(FS, ear)
#         if re.match("\*", ear):
#             #           print ("ear: ",ear)
#             break

#         if len(ea_fields) > 1:
#             EntityAction = ea_fields[0].split("=")
#             EntityActionNames = EntityAction[0].split(" ")
#             EntityName = EntityActionNames[0]

#             EntityName = re.sub("\<", "", EntityName)
#             EntityName = re.sub("\>", "", EntityName)

#             # Create a dictionary of entities for output as list
#             entity_entity[EntityName] = EntityName + ""

#             ActionName = EntityActionNames[1]
#             entity_space_action[NR] = EntityName + " " + ActionName
#             entity_underscore_actions[NR] = EntityName + "_" + ActionName
#             entity_underscore_action = EntityName + "_" + ActionName
#             entity_dot_action = EntityName + "." + ActionName

#             privilege_list = " "

#             if entity_underscore_action in event_list_with_privileges:
#                 privilege_list = event_list_with_privileges[
#                     entity_underscore_action]
#                 privilege_list_string = ', '.join(privilege_list)
#             else:
#                 privilege_list_string = " "

#             #           print ("EntityName: ", EntityName)
#             #           print ("ActionName: ", ActionName)

#             mykeysstring = " ".join((ea_fields))
#             #           print ("mykeysstring: ",mykeysstring)

#             thekeys = re.findall('(?<=KEYS\.)[A-Z_]*', mykeysstring)
#             if thekeys:
#                 #               print(thekeys)
#                 thekeystring = ', '.join(thekeys)
#             else:
#                 thekeystring = " "

#             startout[NR] = "| "
#             endout[NR] = " | " + ActionName + " | " + \
#                 thekeystring + " | " + privilege_list_string + " |"
#             #           print("endout[NR]: ",endout[NR])

#             if privilege_list != " ":
#                 for x in privilege_list:
#                     print("x: %s" % x)
#                     if x in roles_data:
#                         if "USER" in roles_data[x]:
#                             print("Entity.Action: %s" % entity_dot_action)
#                             user_out.append(entity_dot_action)
#                             if EntityName not in user_entity_out:
#                                 user_entity_out.append(EntityName)
#                         if "ENTERPRISE_ADMIN" in roles_data[x]:
#                             ent_admin_out.append(entity_dot_action)
#                             if EntityName not in ent_admin_entity_out:
#                                 ent_admin_entity_out.append(EntityName)

#         if len(ea_fields) == 1:
#             eIndex = NR + 1
#             ENameHeading = ea_fields[0]
#             ENameHeading = re.sub("\{", "", ENameHeading)
#             ENameHeading = re.sub("\n", "", ENameHeading)
#             entityout[eIndex] = ENameHeading
#             entity_for_users[NR] = ENameHeading
#             entityheader_fixcase = ENameHeading
#             entityheader_fixcase = re.sub("_", " ", entityheader_fixcase)
#             entityheader_fixcase = entityheader_fixcase.lower()
#             capital_letter = entityheader_fixcase[:2]
#             capital_letter = capital_letter.upper()
#             rest_of_letters = entityheader_fixcase[2:]
#             entityheader_for_sub = capital_letter + rest_of_letters
#             entityheader_for_sub = re.sub("ip", "IP", entityheader_for_sub)
#             entityheader_for_sub = re.sub("Ssl", "SSL", entityheader_for_sub)
#             entityheader_for_sub = re.sub("ldap", "LDAP", entityheader_for_sub)
#             entityheader[NR] = entityheader_for_sub

#     with open(os.path.join(input_subdir, user_entity_list), 'w') as d:
#         for ueo in sorted(user_entity_out):
#             UserEntityOut = ueo + "\n"
#             d.write(UserEntityOut)

#     with open(os.path.join(input_subdir, ent_admin_entity_list), 'w') as e:
#         for eeo in sorted(ent_admin_entity_out):
#             EntAdminEntityOut = eeo + "\n"
#             e.write(EntAdminEntityOut)

#     with open(os.path.join(input_subdir, entity_list), 'w') as g:
#         for eno in sorted(entity_entity):
#             EntityNameOut = eno + "\n"
#             g.write(EntityNameOut)

#     with open(os.path.join(input_subdir, entity_action_list), 'w') as h:
#         for eao in sorted(entity_action):
#             if re.match("[A-Z]", eao):
#                 EntityActionOut = eao + "\n"
#                 h.write(EntityActionOut)

#     with open(os.path.join(input_subdir, user_entity_action_list), 'w') as j:
#         for ueao in sorted(user_out):
#             UserEntityActionOut = ueao + "\n"
#             j.write(UserEntityActionOut)

#     with open(os.path.join(
#             input_subdir,
#             ent_admin_entity_action_list), 'w') as k:
#         for eeao in sorted(ent_admin_out):
#             EntAdminEntityActionOut = eeao + "\n"
#             k.write(EntAdminEntityActionOut)

#     with open(os.path.join(
#             out_subdir,
#             wiki_entity_action_privileges_file), 'w') as f:
#         header = "|| Entity || Action || Additional Information" + \
#             " || Privileges for Event || \n"
#         f.write(header)
#         NRI = NRSave - 2
#         for s in range(1, NRI):
#             if s in endout:
#                 if s in entityout:
#                     outline = startout[s] + entityout[s] + endout[s] + "\n"
#                     f.write(outline)
#                 else:
#                     outline = startout[s] + endout[s] + "\n"
#                     f.write(outline)
#             else:
#                 outline = "|| h6. " + entityheader[s] + " || || || ||\n"
#                 f.write(outline)


# Calls the main() function
if __name__ == '__main__':
    main()
