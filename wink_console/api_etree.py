#!/usr/bin/python3 -tt
# Process Abiquo wink console
# Remove namespace first!

from lxml import etree

class ResTableRow:
    def __init__(self,a_method_name,a_url_short,a_url_long,a_mt_accept,a_mt_content):
        self.method_name=a_method_name
        self.url_short=a_url_short
        self.url_long=a_url_long
        self.mt_accept=a_mt_accept
        self.mt_content=a_mt_content


def main():
    uri_short = ""
    uri_long = ""
    api_method = ""
    api_mt_accept = ""
    api_mt_content = ""
    uri_store = []

#   tree = etree.parse("sample.xml")
    tree = etree.parse("v30x_wink_console_resources.xml")
#    print("version: ",tree.docinfo.xml_version)
    root = tree.getroot()
    for resource in root:
#        print (len(resource))
        for reschild in resource:
            uri_short = ""
            uri_long = ""
            api_method = ""
            mt_accept = ""
            mt_content = ""
            format_type = ""
            if reschild.tag == ('uri'):
                uri_long = reschild.text
#               print ("uri: ",uri_long)
                uri_short = repLongNames(uri_long)
                api_uri_long = uri_long.strip()
                api_uri_short = uri_short.strip()
                uri_store.append(uri_short)

#               print ("short: ",uri_short)
#               uri_dict_long[uri_short] = uri_long
#               uri_dict[uri_short] = uri_short


            if reschild.tag == ('methods'):
                if len(reschild) > 0:
                    api_method = ""
                    for method in reschild:
                        for apimethod in method:
                            if apimethod.tag in ('name', 'accept-media-types', 'produced-media-types'):                                    
                                if apimethod.text is not None:
                                    api_method_text = apimethod.text
                                    api_method_text = api_method_text.strip()
#                                    if api_method_text is not "OPTIONS":
#                                       print ("API method: ", apimethod.tag,"ok:", apimethod.text)
#                                       short_call = apimethod.text + " " + uri_short
#                                       long_call = apimethod.text + " " + uri_long
#                                       uri_methods[short_call] = short_call
#                                       uri_methods_long[long_call] = long_call

                                    api_method_tag = apimethod.tag
                                    api_method_tag = api_method_tag.strip()
                                    if len(apimethod) > 0:
                                        mt_accept = ""
                                        mt_content = ""
                                        api_mt_content = ""
                                        api_mt_accept = ""
                                        for mt in apimethod:
#                                                print ("mt.text",mt.text)
                                            current_media_type = mt.text
                                            format_list = current_media_type.split('+')
                                            format_type = format_list[-1]
#                                                print ("format",format_type)
                                            full_media_def = format_list[0]
                                            media_def_list = full_media_def.split('.')
                                            media_def = media_def_list[-1]  
#                                                print ("media_def",media_def)
                                            if mt.tag in ('accept-media-type'):
                                                api_mt_content = api_mt_content + " | " + media_def.strip() + " " + format_type.strip()    
                                            if mt.tag in ('produced-media-type'):
                                                api_mt_accept = api_mt_accept + " | " + media_def.strip() + " " + format_type.strip()
                                    uri = api_uri_short 
                                    uri = uri_store[-1]
                                    print(api_method_text," ",uri," ",api_mt_content," ",api_mt_accept)

def repLongNames(auri):
    urd = dict(enterprise='ent',publiccloudregion="pcr",virtualdatacenter='vdc',datacenter='dc',virtual='v',machine='m',template='tmp',appliance='app',configuration='config',repositorie='repo',repository='repo',network='nw',privilege='priv',remoteservices="rs",hardware="hw")
    for f, r in urd.items():
  	    aurir = auri.replace(f,r)
  	    auri = aurir
    return auri 



if __name__ == '__main__':
  main()

