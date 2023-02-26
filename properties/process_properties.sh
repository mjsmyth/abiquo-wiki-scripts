#! /bin/sh
# Read the github properties file
# Discard all lines that are not property=default
# sort file in alpha order
#
# Based on http://shrubbery.mynetgear.net/c/display/W/Reading+Java-style+Properties+Files+with+Shell#ReadingJava-stylePropertiesFileswithShell-Method2reloaded-UseAWK
# This is a dodgy awk script that reads the property file from $1 and redirects print to a wiki storage format output and other output files and puts standard out in $2
# Sample call: ./process_properties.sh ../platform/system-properties/src/main/resources/abiquo.properties pout.txt
# Note that $2 (in above example pout.txt) will be an empty file. The redirected output files are in the output_files folder and they are:
# wiki_properties_2014-10-29.txt - wiki storage format for pasting in the Abiquo Configuration Properties page
# properties_api.txt, properties_rs.txt, properties_v2v.txt, properties_oa.txt - sample properties files for the Abiquo install profiles
# Attach the sample files to the Abiquo Configuration Properties page

cat $1 | gawk 'BEGIN{ 
# Record separator is blank line(s)
  RS=""; 
# Field separator is new line
  FS="\n"; 
  outputLine[0]=""; 
  gitRange = "";
  gitPropName = ""; 
  gitDefault = ""; 
  gitValues[0] = "";
  rangeValues[0] = "";
  gitOptional[0]="";
  gitTotProp = 0;
  IGNORECASE = 1;
  myLine = "";
  gitPropNameSplit[0] = "";
  gitPropNameCat[0] = "";
  headerProf[0] = "";
  td = "2014-10-29"
  

  fn_api = "properties_api_" td ".txt";
  fn_rs = "properties_rs_" td ".txt";
  fn_v2v = "properties_v2v_" td ".txt";
  fn_oa = "properties_oa_" td ".txt";
  
  gitPrintStars = "################################################################################";
  gitPrintIntro = "#### This is a sample abiquo.properties file for ";      
  gitPrintEnd =   "     ####";
  gitHubWarn[0] = "#### This file is a sample only and Abiquo recommends that the customer     ####";
  gitHubWarn[1] = "#### should always use the properties file provided in the installation.    ####";
  gitHubWarn[2] = "#### In this file, required properties are uncommented and optional         ####";
  gitHubWarn[3] = "#### properties are commented. Default values are always supplied but       ####";
  gitHubWarn[4] = "#### they are not customized here as they are in the installer. For         ####";
  gitHubWarn[5] = "#### example, in this file, an IP address may be localhost, instead of the  ####";
  gitHubWarn[6] = "#### installer value.                                                       ####";
  gitHubWarn[7] = "#### http://wiki.abiquo.com/display/ABI26/Abiquo+Configuration+Properties   ####";

    
  linkNL   = "\n" ; 
  linkAPIA = "<ac:link><ri:attachment ri:filename=\"" fn_api "\" /><ac:link-body><ac:image ac:thumbnail=\"true\" ac:width=\"30\">";
  linkAPIB = "<ri:attachment ri:filename=\"v26_symbol_api_transparent.png\" /></ac:image></ac:link-body></ac:link>";
  
  linkRSA  = "<ac:link><ri:attachment ri:filename=\"" fn_rs "\" /><ac:link-body><ac:image ac:thumbnail=\"true\" ac:width=\"30\">";
  linkRSB = "<ri:attachment ri:filename=\"v26_symbol_rs_transparent.png\" /></ac:image></ac:link-body></ac:link>";
  
  linkV2VA = "<ac:link><ri:attachment ri:filename=\"" fn_v2v "\" /><ac:link-body><ac:image ac:thumbnail=\"true\" ac:width=\"30\">";
  linkV2VB = "<ri:attachment ri:filename=\"v26_symbol_v2v_transparent.png\" /></ac:image></ac:link-body></ac:link>";
  
  linkOAA  = "<ac:link><ri:attachment ri:filename=\"" fn_oa "\" /><ac:link-body><ac:image ac:thumbnail=\"true\" ac:width=\"30\">";
  linkOAB  = "<ri:attachment ri:filename=\"v26_symbol_oa_transparent.png\" /></ac:image></ac:link-body></ac:link>";
  
  print "<table>\n<tbody>\n<tr><th class=\"warning\" data-highlight-class=\"warning\">  <p>Property</p></th>" >> "output_files/wiki_properties_2014-10-29.txt";
  print "<th class=\"warning\" data-highlight-class=\"warning\"><p>Default</p></th>" >> "output_files/wiki_properties_2014-10-29.txt";
  print "<th class=\"warning\" data-highlight-class=\"warning\"><p>Range</p></th>" >> "output_files/wiki_properties_2014-10-29.txt";
  print "<th class=\"warning\" data-highlight-class=\"warning\"><p>Description</p></th>" >> "output_files/wiki_properties_2014-10-29.txt";
  print "<th class=\"warning\" colspan=\"1\" data-highlight-class=\"warning\">" linkAPIA linkAPIB "</th>" >> "output_files/wiki_properties_2014-10-29.txt";
  print "<th class=\"warning\" colspan=\"1\" data-highlight-class=\"warning\">" linkRSA linkRSB "</th>" >> "output_files/wiki_properties_2014-10-29.txt";
  print "<th class=\"warning\" colspan=\"1\" data-highlight-class=\"warning\">" linkV2VA linkV2VB "</th>" >> "output_files/wiki_properties_2014-10-29.txt";
  print "<th class=\"warning\" colspan=\"1\" data-highlight-class=\"warning\">" linkOAA linkOAB "</th>" >> "output_files/wiki_properties_2014-10-29.txt";
  print "<th class=\"warning\" colspan=\"1\" data-highlight-class=\"warning\">Info</th></tr>" >> "output_files/wiki_properties_2014-10-29.txt";
  
  
  print gitPrintStars > "output_files/" fn_api;
  print gitPrintIntro "API / SERVER          " gitPrintEnd >> "output_files/" fn_api;
  print gitPrintStars "\n\n" >> "output_files/" fn_api;              
              
  print gitPrintStars > "output_files/" fn_rs;
  print gitPrintIntro "REMOTE SERVICES       " gitPrintEnd >> "output_files/" fn_rs;
  print gitPrintStars "\n\n" >> "output_files/" fn_rs;              
              
  print gitPrintStars > "output_files/" fn_v2v;
  print gitPrintIntro "V2V (REMOTE SERVICES) " gitPrintEnd >> "output_files/" fn_v2v;
  print gitPrintStars "\n\n" >> "output_files/" fn_v2v;              
              
  print gitPrintStars > "output_files/" fn_oa;
  print gitPrintIntro "OUTBOUND API          " gitPrintEnd >> "output_files/" fn_oa;
  print gitPrintStars "\n\n" >> "output_files/" fn_oa;              

}
{
  if ($1 ~ /#####/)
  {
            testHeader = $1;
            if (testHeader ~ "MULTIPLE PROFILES")
            {
              next;
            }
            else
            {  
              if (testHeader ~ "SERVER" )
                {
#                 headerProf[1] = "<strong>A</strong>"; 
                  headerProf[1] = linkAPIA linkAPIB;
                 }
               else 
                {
                  headerProf[1] = " ";
                }     
               if (testHeader ~ "REMOTESERVICES")
                {
#                 headerProf[2] = "<strong>R</strong>";
                  headerProf[2] = linkRSA linkRSB;                 
                }
              else
               {
                 headerProf[2] = " ";
               }
               if (testHeader ~ "V2VSERVICES")
               {
#                 headerProf[3] = "<strong>V</strong>";
                  headerProf[3] = linkV2VA linkV2VB;
               }
              else
               {
                headerProf[3] = " ";
               }
               if (testHeader ~ "M OUTBOUND API")
               {
#                 headerProf[4] = "<strong>O</strong>";
                  headerProf[4] = linkOAA linkOAB;
               }
              else
               {
                headerProf[4] = " ";
               }
             }  
  }
  else
  {
# If the last field in the record has an "=" in it
     if ($NF ~ /=/) 
         { 
            if (headerProf[1] != " ")
              {
                print $0 >> "output_files/" fn_api;
                print " " >> "output_files/" fn_api;
              }
              
            if (headerProf[2] != " ")
              {
                print $0 >> "output_files/" fn_rs; 
                print " " >> "output_files/" fn_rs;
              } 
              
            if (headerProf[3] != " ")
              {
                print $0 >> "output_files/" fn_v2v;
                print " " >> "output_files/" fn_v2v;
              }
              
            if (headerProf[4] != " ")
              {
                print $0 >> "output_files/" fn_oa; 
                print " " >> "output_files/" fn_oa;
              }   

            gitValuesLine = $NF;
            split(gitValuesLine,gitValues,/\=/);

            gitPropName = gitValues[1];
            gsub(/^ */,"",gitPropName);
            gsub(/ *$/,"",gitPropName);
# Check if the value is commented out = optional 
            if (gitPropName ~ /^#/)
            {
#                print "Optional";
                 gsub(/^#/,"",gitPropName);            
                 gsub(/^ */,"",gitPropName);    
                 gitOptional[gitPropName] = "(*)";
            }
            else
            {
                  gitMandatory[gitPropName] = "(*)";
#                  print "Mandatory";
            } 
            gitDefault = "";
# The default value may have some more equals signs in it, so reconcatenate them
            if (gitValues[2] ~ /[A-Za-z0-9\/]/)
            {  
              gitDefault = gitValues[2];
              gitTotProp = 0;
              for (gindex in gitValues)
              {
                  gitTotProp = gitTotProp + 1;
#                  print "gindex: " gindex;
              }
              if (gitTotProp > 2) 
              {
                for (giti = 3; giti <= gitTotProp; giti ++)
                 {
                    gitDefault = gitDefault "=" gitValues[giti];   
                  } 
              }    
#             print "gitDefault: " gitDefault;
# Replace leading and trailing spaces in the default with nothing
              gsub(/^ */,"",gitDefault);
              gsub(/ *$/,"",gitDefault);
# Escape { in the default for the wiki               
              if (gitDefault ~ "\{")
              {
                 gsub("\{","\\\{",gitDefault);
              }   
# Replace developer stuff
              if (gitPropName == "abiquo.datacenter.id")
              {
                 gsub("default","Abiquo",gitDefault);
              }   
              gsub("127.0.0.1","\\\&lt;IP-repoLoc\\\&gt;",gitDefault);
              gsub("localhost","127.0.0.1",gitDefault);
#              gsub("10.60.1.4","\\\&lt;IP-mail\\\&gt;",gitDefault);
              gsub("10.60.1.91","\\\&lt;IP-storagelink\\\&gt;",gitDefault);
              
              gitPropDefault[gitPropName] = gitDefault;
#              print "Valid default";


# Divide properties into categories based on the second part of the name


            }
            else
            {
#              print "Default not valid";
                gitDefault = " ";
            }   
            # Replace < and > for storage format
              if (gitDefault ~ "\<")
              {
                 gsub("\<","\\\&lt;",gitDefault);
              } 
              if (gitDefault ~ "\>")
              {
                 gsub("\>","\\\&gt;",gitDefault);
              }  
#           print "Property name: " gitPropName;
#           print "Property default: " gitDefault; 
     
            outputDesc = "";
            finalDesc = "";
            for (indy = 1; indy < NF; indy ++)
             {
                 descHash = $indy;
                 gsub(/^#/,"",descHash);            
                 outputDesc = outputDesc descHash;
             } 
             # Replace < and > for storage format
              if (outputDesc ~ "\<")
              {
                 gsub("\<","\\\&lt;",outputDesc);
              } 
              if (outputDesc ~ "\>")
              {
                 gsub("\>","\\\&gt;",outputDesc);
              } 
# Get the range off the end of the description and stick it in a separate column          
           split(outputDesc,rangeValues,"Range: ");
# Check there is something vaguely alphanumeric in the range           
           if (rangeValues[2] ~ /[A-Za-z0-9]/)
           {
             gitRange = rangeValues[2];
             finalDesc = rangeValues[1];
           } 
           else 
           {
             gitRange = " ";
             finalDesc = rangeValues[1];
           }   
           split(gitPropName,gitPropNameSplit,/\./);
           gitPropNameCat[gitPropName] = gitPropNameSplit[2];
           propSort[gitPropName] = gitPropName;     
           outputLine[gitPropName] = "<tr><td><p> " gitPropName " </p></td><td><p> " gitDefault " </p></td><td><p> " gitRange " </p></td><td><p> " finalDesc " </p></td><td><p> " headerProf[1] " </p></td><td><p> " headerProf[2] " </p></td><td><p> " headerProf[3] " </p></td><td><p> " headerProf[4] " </p></td><td><p></p></td></tr>" ; 
#            outputLine[gitPropName] = "| " gitPropName " | " gitDefault " | " gitRange " | " finalDesc " | " headerProf[1] " | " headerProf[2] " | " headerProf[3] " | " headerProf[4] " | " gitOptional[gitPropName] " | ";      
      }
     else
      {
#       outputPrep[NR] = "noprint";
      } 
    } 
}
END{
    repNum = asort(propSort);
    for (indo = 1; indo <= repNum; indo ++) 
      {
          myLine = propSort[indo];
          if (indo == 1)
          {
            print "<tr><th class=\"warning\" colspan=\"9\" data-highlight-class=\"warning\"><p><h6>" gitPropNameCat[myLine] "</h6></p></th>" >> "output_files/wiki_properties_2014-10-29.txt" ;
 #           for (j=1;j<5;j++)
 #              {
 #                print "<th class=\"warning\" data-highlight-class=\"warning\"><p><strong></strong></p></th><th class=\"warning\" data-highlight-class=\"warning\"><p><strong>" "</strong></p></th>" >> "output_files/wiki_properties_2014-10-29.txt" ;
 #              }
            print "</tr>" >> "output_files/wiki_properties_2014-10-29.txt";
            }
          
          if (indo > 1)
          {
            myPrevLine = propSort[(indo-1)];
            if (gitPropNameCat[myLine] != gitPropNameCat[myPrevLine])
            {
               print "<tr><th class=\"warning\" data-highlight-class=\"warning\"><p><h6>" gitPropNameCat[myLine] "</h6></p></th>" >> "output_files/wiki_properties_2014-10-29.txt";
               for (j=1;j<5;j++)
               {
                 print "<th class=\"warning\" data-highlight-class=\"warning\"><p><strong></strong></p></th><th class=\"warning\" data-highlight-class=\"warning\"><p><strong>" "</strong></p></th>" >> "output_files/wiki_properties_2014-10-29.txt" ;
               }
              print "</tr>" >> "output_files/wiki_properties_2014-10-29.txt";
            }
          }     
          print outputLine[myLine] >> "output_files/wiki_properties_2014-10-29.txt";     
      }
    print "</tbody>\n</table>" >> "output_files/wiki_properties_2014-10-29.txt";
}' >$2 
