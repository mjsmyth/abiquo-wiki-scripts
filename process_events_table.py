#!/usr/bin/python3 -tt
# Use the new generated files to create the events table

import re
import os
from datetime import datetime


SEVERITY = [("INFO", "(i)"), ("WARN", "(!)"), ("ERROR", "(-)")]
outputSubdir = "output_files"
todaysDate = datetime.today().strftime('%Y-%m-%d')
wikiEventTracerFile = "wiki_event_tracer_all_" + todaysDate + ".txt"


def main():
    header = "|| Entity || Action || Severity || Tracer || Event privileges ||\n"

    # Read the entity action file
    tracerEntitiesDir = "../platform/api/src/main/generated"
    tracerEntitiesFileName = "tracer.entities"
    entityAllActionsFile = [eea.strip() for eea in open(os.path.join(
        tracerEntitiesDir, tracerEntitiesFileName))]

    # Read the tracer properties file
    tracerPropertiesDir = "../platform/api/src/main/generated"
    tracerPropertiesFileName = "tracer-properties.doc"
    tracerPropertyFile = [tp.strip() for tp in open(os.path.join(
        tracerPropertiesDir, tracerPropertiesFileName))]

    # Read the event security properties file
    eventSecurityPropertiesDir = "../platform/api/src/main/resources/events"
    eventSecurityPropertiesFileName = "events-security.properties"
    eventSecurityPropertyFile = [es.strip() for es in open(os.path.join(
        eventSecurityPropertiesDir, eventSecurityPropertiesFileName))]

    tracerList = []
    entityActionList = []
    securityDict = {}

    # Compile the entity_action and create list sorted from longest to shortest
    # A row looks like this: ALARM = CREATE,DELETE,MODIFY
    for entityAllActionRow in entityAllActionsFile:
        entityActionsList = entityAllActionRow.split("=")
        entity = entityActionsList[0].strip(" ")
        actionsList = entityActionsList[1].strip(" ").split(",")
        for action in actionsList:
            entityAction = entity + "_" + action
            entityActionList.append((entity, action, entityAction))
    # Event security file looks like this:
    # MANAGE_DEVICES=DEVICE.CREATE, DEVICE.DELETE
    for eventSecurityRow in eventSecurityPropertyFile:
        securityList = eventSecurityRow.split("=")
        entityActionPrivilege = securityList[0]
        entityDotActionSecurityList = securityList[1].split(", ")
        for entityDotAction in entityDotActionSecurityList:
            if entityDotAction not in securityDict:
                securityDict[entityDotAction] = []
            securityDict[entityDotAction].append(entityActionPrivilege)

    for tracerPropertyRow in tracerPropertyFile:
        tracerPropertyList = tracerPropertyRow.split("=")
        tracerPropertyKey = tracerPropertyList[0].strip(" ")
        tracerPropertyMessage = ("=".join(tracerPropertyList[1:])).strip(" ")
        # Replace or escape characters that are problematic for the wiki
        tracerPropertyMessage = re.sub("\{", "", tracerPropertyMessage)
        tracerPropertyMessage = re.sub("\}", "", tracerPropertyMessage)
        tracerPropertyMessage = re.sub("\[", "(", tracerPropertyMessage)
        tracerPropertyMessage = re.sub("\]", ")", tracerPropertyMessage)
        tracerPropertyMessage = re.sub(":", " -", tracerPropertyMessage)
        # replace spelling mistakes in parameters temporarily
        spellingMistakes = {"dataventer": "datacenter",
                            "mahine": "machine",
                            "tempalte": "template",
                            "nackup": "backup",
                            "Plna": "Plan"}
        for spellingMistake, correction in spellingMistakes.items():
            tracerPropertyMessage = tracerPropertyMessage.replace(spellingMistake, correction)
        for (entity, action, entityAction) in entityActionList:
            if entityAction in tracerPropertyKey:
                # print("tracerPropertyKey: ", tracerPropertyKey)
                # print("entity_action: ", entityAction)
                entityPlusAction = entity + "." + action
                if entityPlusAction in securityDict:
                    privileges = ", ".join(securityDict[entityPlusAction])
                for (severity, severityCode) in SEVERITY:
                    # print("Looking for severity: ", severity)
                    # Look for severity type (INFO, WARNING, ERROR)
                    if severity in tracerPropertyKey:
                        # print("severity: ", severity)
                        tracerLine = "| " + entity + " | " + action + \
                            " | " + severityCode + " | " + \
                            tracerPropertyMessage + " | " + \
                            privileges + " |\n"
                        tracerList.append(tracerLine)
    # Variable to check if new group for header row
    lastEntity = " "
    with open(os.path.join(outputSubdir, wikiEventTracerFile), 'w') as f:
        f.write(header)
        sortedTracerList = sorted(tracerList)
        for tracer in sortedTracerList:
            tracerEntity = tracer.split("|")[1].strip()
            if tracerEntity != lastEntity:
                tracerHeaderLine = "|| " + tracerEntity.replace("_", " ").capitalize() + " ||  ||  ||  ||  ||\n"
                f.write(tracerHeaderLine)
                lastEntity = tracerEntity[:]
            f.write(tracer)


# Calls the main() function
if __name__ == '__main__':
    main()
