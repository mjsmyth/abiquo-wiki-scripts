#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# Metrics push
# ============
# Environment: With access to internet
# Input:
# - Mandatory: 
#   -- an API token for auth
#   -- API url (https://abiquo.example.com/api)
# - Optional: VApp name, source metric names, create metric names
#
# Requires a deployed VApp with a scaling group
#
# 1. Gets the VApp by name
# 2. Gets avg metrics for all VMs in the cloud
# 3. Create metrics for Vapp and Scaling group in VApp
#
# TODO: Optionally create metrics for all VApps in VDC
# and all scaling groups in the Vapps.
#
# Dependencies:
# abiquo-api installed with pip3
#
# import json
from abiquo.client import Abiquo
from abiquo.auth import TokenAuth
from abiquo.client import check_response
from itertools import cycle
import json
import random
# For test environment disable SSL warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def createMetadata(entity, metName):
    # Create metadata for the metrics that don't have it
    mddesc = entity + metName
    MetricMetadata = {'name': metName,
                      'description': mddesc,
                      'unit': 'percent'
                      }

    code, newMd = entity.follow('metricsmetadata').post(
        headers={'content-type':
                 'application/vnd.abiquo.metricmetadata+json',
                 'accept':
                 'application/vnd.abiquo.metricmetadata+json'
                 },
        data=json.dumps(MetricMetadata))
    print("Create metadata for", metName, "Response code is: ", code)
    return code


def getMetadata(entity):
    print ("entity name: ", entity.name)
    code, entitymd = entity.follow('metricsmetadata').get(
        headers={'Accept':
                 'application/vnd.abiquo.metricsmetadata+json'})
    print("Get MD of ", entity.name, "Response code is: ", code)
    return (code, entitymd)


def getAndCreateMetadata(entity, metricsCreate):
    code, entityMd = getMetadata(entity)
    metNameWithMetadata = []
    # Get list of names of metrics names with metadata
    for md in entityMd:
        metNameWithMetadata.append(md.name)

    # Build list of metrics to create that don't have metadata
    metNamesNoMd = list(filter(
        lambda mcnmd: mcnmd not in metNameWithMetadata, metricsCreate))

    # Create metadata for the metrics that don't have it
    for metName in metNamesNoMd:
        ocode = createMetadata(entity, metName)
        print ("Created metadata for", entity, "Code: ", ocode)

    code, entityMd = getMetadata(entity)
    return (code, entityMd)


def getMetricsFromVMs(vmsOn, metricsSource):
    for virtualMachine in vmsOn:
        code, metrics = getMetadata(virtualMachine)
        check_response(200, code, metrics)
        print("Get VM metrics, Response code is: ", code)
        print("VM name: ", virtualMachine.name)
        for vmLink in virtualMachine.json["links"]:
            if vmLink["rel"] == "virtualappliance":
                vappName = vmLink["title"]
                print("Belongs to VApp: ", vappName)

        metSource = list(filter(lambda me: me.name in metricsSource, metrics))
        metricsList = []
        for met in metSource:
            code, ame = met.metric.get(
                headers={'Accept':
                         'application/vnd.abiquo.metric+json'})
            check_response(200, code, ame)
            print("Get VM metric data, Response code is: ", code)
            if ame.datapoints:
                print("metric datapoints: ", ame.datapoints)
                metricsList.append(ame.datapoints)
        return metricsList


def getVappByName(inputVappName, vdcsList):
    # Assuming a unique name but just returning first instance of name
    for vdc in vdcsList:
        code, inputVapps = vdc.virtualappliances.get(
            headers={'accept':
                     'application/vnd.abiquo.virtualappliances+json'},
            params={'has': inputVappName})
        print("Get virtual appliances. Response code is: ", code)
        if inputVapps:
            for vapp in inputVapps:
                print("VApp name: ", vapp.name)
                return vapp


def pushDatapoints(entity, metricsCreate, dpPool):
    code, entMdList = getAndCreateMetadata(entity, metricsCreate)
    print("Get metadata", entity.name, "Response code is: ", code)
    for entm in entMdList:
        if entm.name in metricsCreate:
            code, resp = entm.follow('metric').post(
                headers={'content-type':
                         'application/vnd.abiquo.datapoints+json',
                         'accept':
                         'text/json,application/json'},
                data=json.dumps(next(dpPool)))
            print("Create metric datapoints for ", entm.name,
                  " Response code is: ", code)


def main():
    # Abiquo API token
    token = input("Enter token: ")
    apiUrl = input("Enter API URL: ")
    # apiUrl = "https://abiquo.example.com/api"
    inVapp = input("Enter a unique VApp name: ")
    # inVapp = "vapp_mjs"
    api = Abiquo(apiUrl, auth=TokenAuth(token), verify=False)
    metricsSource = ["abq-cpu_usage", "abq-ram_usage"]
    metricsCreate = ["metric_01", "metric_02", "metric_03"]
    # Get the virtual datacenters from the cloud
    code, vdcsList = api.cloud.virtualdatacenters.get(
        headers={'accept': 'application/vnd.abiquo.virtualdatacenters+json'})
    print("Get virtual datacenters. Response code is: ", code)

    # Get the VApp from the VDCs by its unique name
    theVapp = getVappByName(inVapp, vdcsList)
    # print ("vapp json", theVapp.json)

    # Get the Scaling groups from the VApp
    code, scalingGroups = theVapp.follow("scalinggroups").get()

    getAndCreateMetadata(theVapp, metricsCreate)
    for scalingGroup in scalingGroups:
        print ("sgname", scalingGroup.name)
        getAndCreateMetadata(scalingGroup, metricsCreate)

    # Get the virtualmachines from the cloud to use their metrics
    # as the source of the fake metrics
    code, virtualMachinesList = api.cloud.virtualmachines.get(
        headers={'accept': 'application/vnd.abiquo.virtualmachines+json'})
    check_response(200, code, virtualMachinesList)
    print("Get virtualmachines. Response code is: ", code)

    # Get selected metrics from all of the user's VMs that are powered ON
    vmsOn = list(filter(lambda vm: vm.state == "ON", virtualMachinesList))
    metricsList = getMetricsFromVMs(vmsOn, metricsSource)

    # Create some datapoints for the metrics
    datapointsList = []
    metPool = cycle(metricsList)
    for mc in metricsCreate:
        datapoints = next(metPool)["average"][:]
        for dp in datapoints:
            dp["value"] = ((dp["value"] + random.random()) * 50) % 100
        datapointData = {'dimensions': {},
                         'links': [],
                         'collection': datapoints}
        datapointsList.append(datapointData)

    dpPool = cycle(datapointsList)
    pushDatapoints(theVapp, metricsCreate, dpPool)
    pushDatapoints(scalingGroup, metricsCreate, dpPool)


# Calls the main() function
if __name__ == '__main__':
    main()
