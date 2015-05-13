#!/usr/bin/python3 -tt
# Process Abiquo wink console
# Remove namespace first!

from lxml import etree

def main():
    uri_short = ""
    uri_long = ""
    uri_dict_long = {}
    uri_dict = {}
    uri_methods = {}
    uri_methods_long = {}
    uri_methods_media_types = {}

#   tree = etree.parse("sample.xml")
    tree = etree.parse("v30x_wink_console_resources.xml")
#    print("version: ",tree.docinfo.xml_version)
    root = tree.getroot()
    for resource in root:
#        print (len(resource))
        for reschild in resource:
             if reschild.tag == ('uri'):
                  uri_long = reschild.text
#                  print ("uri: ",uri_long)
                  uri_short = repLongNames(uri_long)
#                  print ("or: ",uri_short)
                  uri_dict_long[uri_short] = uri_long
                  uri_dict[uri_short] = uri_short

             if reschild.tag in ('methods'):
                  if len(reschild) > 0:
                      for method in reschild:
                          url_methods_list = []
                          for apimethod in method:
                              if apimethod.tag in ('name', 'accept-media-types', 'produced-media-types'):                                    
                                  if apimethod.text is not None:
                                      if apimethod.text is not 'OPTIONS':
                                          print ("API method: ", apimethod.tag,"ok:", apimethod.text)
                                          short_call = apimethod.text + " " + uri_short
                                          long_call = apimethod.text + " " + uri_long
                                          uri_methods[uri_short] = short_call

                                          if len(apimethod) > 0:
                                              for mt in apimethod:
                                                  if mt.tag in ('accept-media-type'):
                                                      url_methods_media_types[]
                                                  if mt.tag in ('produced-media-type'):
                                                      print ("ha: ", mt.tag, "ok: ", mt.text)

                           
   
       

def repLongNames(auri):
      urd = dict(enterprise='ent',virtualdatacenter='vdc',datacenter='dc',virtual='v',machine='m',template='tmp',appliance='app',repositorie='repo',repository='repo',network='nw',privilege='priv')
      for f, r in urd.iteritems():
  	      aurir = auri.replace(f,r)
  	      auri = aurir
      return auri 



if __name__ == '__main__':
  main()

