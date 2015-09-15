#!/usr/bin/python3 -tt
# Process Abiquo wink console
# Remove namespace first!

from lxml import etree
import re

class ResTableRow:
    def __init__(self,a_method_name,a_url_long,a_mt_accept,a_mt_content):
        self.method_name=a_method_name
        self.url_long=a_url_long
        self.mt_accept=a_mt_accept
        self.mt_content=a_mt_content
    
    def printrow(self):
        wiki_mt_accept = self.mt_accept
        wiki_mt_content = self.mt_content
        print_mt_accept = dowikimarkup(wiki_mt_accept)
        print_mt_content = dowikimarkup(wiki_mt_content)          
        print("| ",self.method_name," | ",self.url_long," | ",print_mt_accept," | ",print_mt_content, " |")


def main():
    api_uri_long = ""
    api_uri_short = ""
    api_method_name = ""
    api_mt_accept = []
    api_mt_content = []
    media_def = ""   
    format_type = ""
    table_row_list = []

#   tree = etree.parse("sample.xml")
    tree = etree.parse("v36_wink_console_resources.xml")
#    print("version: ",tree.docinfo.xml_version)
    root = tree.getroot()
    for resource in root:
#        print (len(resource))
        for reschild in resource:
            if reschild.tag == ('uri'):
                api_uri_long = reschild.text
                api_uri_long = api_uri_long.strip()
#                print ("uri: ",uri_long)
#                api_uri_wiki = repLongNames(api_uri_wiki)
                api_uri_wiki = repVars(api_uri_long)
                api_uri_wiki = repBadChars(api_uri_wiki)

            if reschild.tag == ('methods'):
                if len(reschild) > 0:
                    format_type = ""
                    media_def = ""
                    for method in reschild:
                        for apimethod in method:
                            if apimethod.tag == 'name':
                                if apimethod.text is not None:
                                    api_method_name = apimethod.text
                                    api_method_name = api_method_name.strip()
                                    api_mt_content = []
                                    api_mt_accept = []
                                    media_def = ""
                                    format_type = ""

                            if apimethod.tag in ('accept-media-types','produced-media-types'):                                    
                                if apimethod.text is not None:
                                    api_method_text = apimethod.text
                                    api_method_text = api_method_text.strip()
                                    api_method_tag = apimethod.tag
                                    api_method_tag = api_method_tag.strip()

                                    if len(apimethod) > 0:
                                        for mt in apimethod:
#                                            print ("mt.text",mt.text)
                                            current_media_type = mt.text
                                            format_list = current_media_type.split('+')
                                            if len(format_list) == 1:
                                                format_list = current_media_type.split("/")
                                            format_type = format_list[-1]
#                                                    print ("format",format_type)
                                            full_media_def = format_list[0]
                                            media_def_list = full_media_def.split('.')
      
                                            media_def = media_def_list[-1]  
#                                                print ("media_def",media_def)
                                            compound_media = media_def + " " + format_type
                                            if mt.tag in ('accept-media-type'):
                                                if compound_media not in api_mt_content:
                                                    api_mt_content.append(compound_media)

                                            if mt.tag in ('produced-media-type'):
                                                if compound_media not in api_mt_accept:
                                                    api_mt_accept.append(compound_media)
#                                                api_mt_accept.append(media_def)
#                                                api_mt_accept.append(format_type)

#                                                api_mt_accept.append(media_def,format_type)
#                                                api_mt_accept = api_mt_accept + " | " + media_def.strip() + " " + format_type.strip() 
                        uri = api_uri_wiki
                        if api_method_name not in ('OPTIONS'):     
#                            print(api_method_name," ",uri," ",api_mt_content," ",api_mt_accept)
                            r = ResTableRow(api_method_name,uri,api_mt_content,api_mt_accept)
                            r.printrow()

def repLongNames(auri):
    urd = dict(enterprise='ent',publiccloudregion="pcr",virtualdatacenter='vdc',datacenter='dc',virtual='v',machine='m',template='tmp',appliance='app',configuration='config',repositorie='repo',repository='repo',network='nw',privilege='priv',remoteservices="rs",hardware="hw")
    for f, r in urd.items():
  	    aurir = auri.replace(f,r)
  	    auri = aurir
    return auri 

def repBadChars(auri):
    aurir = auri.replace("{","(")
    auris = aurir.replace("}",")")
    auri = auris
    return auri  

def repVars(auri):
    urd = dict(volume='vol',templateDefinitionLis="tmpDefList",templateDefinition='tmpDef',virtualmachine='vm',enterprise='ent',publiccloudregion='pcr',virtualdatacenter='vdc',datacenter='dc',machine='m',virtualmachinetemplate='vmtmp',virtualappliance='vapp',configuration='config',datacenterrepository='dcrepo',enterpriserepository='entrepo',publicnetwork='publicnw',privatenetwork='privatenw',externalnetwork='externalnw',privilege='priv',remoteservice="rs",conversion="conv",hardwareprofile="hwprofile",location="loc",backup="bkp")
    for f,r in urd.items():
        g = "{" + f + "}"
        h = "(" + r + ")"
        aurir = auri.replace(g,h)
        auri = aurir
    return auri  


def dowikimarkup(mediatypeparm):
    store_mta = []
    store_mt_accept = ""
    for mta in mediatypeparm:
        mts = mta.split(" ")
        if mts[0] in store_mta:
            if mts[1] == "xml":
                store_mt_accept = store_mt_accept + " (*b) "
            elif mts[1] == "json":
                store_mt_accept = store_mt_accept + " (*r) "
            else:
                store_mt_accept = store_mt_accept + mts[1] 
        else:
            store_mt_accept = store_mt_accept + " " + mts[0] 
            if mts[1] == "xml":
                store_mt_accept = store_mt_accept + " (*b) "
            elif mts[1] == "json":
                store_mt_accept = store_mt_accept + " (*r) "
            else:
                store_mt_accept = store_mt_accept + mts[1] 
            store_mta.append(mts[0]) 
    mediatypeparm = store_mt_accept    
    return mediatypeparm         

if __name__ == '__main__':
  main()

