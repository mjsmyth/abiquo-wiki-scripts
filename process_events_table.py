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
    header = "|| Entity || Action || Severity || Tracer ||\n"

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

    tracerList = []
    entityActionList = []
    # Compile the entity_action and create list sorted from longest to shortest
    # A row looks like this: ALARM = CREATE,DELETE,MODIFY
    for entityAllActionRow in entityAllActionsFile:
        entityActionsList = entityAllActionRow.split("=")
        entity = entityActionsList[0].strip(" ")
        actionsList = entityActionsList[1].strip(" ").split(",")
        for action in actionsList:
            entityAction = entity + "_" + action
            entityActionList.append((entity, action, entityAction))
    lastEntity = " "
    for tracerPropertyRow in tracerPropertyFile:
        tracerPropertyList = tracerPropertyRow.split("=")
        tracerPropertyKey = tracerPropertyList[0].strip(" ")
        tracerPropertyMessage = ("".join(tracerPropertyList[1:])).strip(" ")
        tracerPropertyMessage = re.sub("\{", "", tracerPropertyMessage)
        tracerPropertyMessage = re.sub("\}", "", tracerPropertyMessage)
        for (entity, action, entityAction) in entityActionList:
            if entityAction in tracerPropertyKey:
                if entity != lastEntity:
                    tracerHeaderLine = "|| " + entity.capitalize() + " ||  ||  ||  ||\n"
                    tracerList.append(tracerHeaderLine)
                    lastEntity = entity[:]
                print("tracerPropertyKey: ", tracerPropertyKey)
                print("entity_action: ", entityAction)
                for (severity, severityCode) in SEVERITY:
                    print("Looking for severity: ", severity)
                    # Look for severity type (INFO, WARNING, ERROR)
                    if severity in tracerPropertyKey:
                        print("severity: ", severity)
                        tracerLine = "| " + entity + " | " + action + \
                            " | " + severityCode + " | " + \
                            tracerPropertyMessage + " |\n"
                        tracerList.append(tracerLine)

    with open(os.path.join(outputSubdir, wikiEventTracerFile), 'w') as f:
        f.write(header)
        for tracer in tracerList:
            f.write(tracer)


# Calls the main() function
if __name__ == '__main__':
    main()
