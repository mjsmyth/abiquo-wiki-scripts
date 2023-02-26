#! /bin/sh
# create a set of tables of events and actions 
# Input file should be platform/model/event-model-transport/src/main/java/com/abiquo/event/model/enumerations/EntityAction.java
# Output file should be output_files/wiki_events.txt
# Note that I have hacked this program to make it leave out the java muck surrounding the enumerations!
# If there are any problems: it uses RS = Master, and checks for * in records, and doesn't print headers or details of the first record and last two records! 
# NOTE that this script produces two other output files - entity_action_list.txt, which is an input to the tracer processing scripts
# and entity_list.txt which is a list of all entities as a starting point for the events and tracer tables for users... 
# actually now I think about it, the user events have "USER" maybe this isn't necessary... aagh
# ./process_events.sh ../platform/model/event-model-transport/src/main/java/com/abiquo/event/model/enumerations/EntityAction.java output_files/wiki_events.txt
#
# Note that the following comments are out of date:
# Convert EventType.java to Confluence Wiki Format
# Note that it is best to cut the java code from the beginning and end of the file as that is not included in the scope of this script
# Read EventType.java file $1 and write to wiki output $2
# Mark comments starting with // as header records
# Strip whitespace in the file
# Set the record separator as "), "
# Print the first field of lines with one field beginning with // as h5. in wiki format after stripping non-numerics, then print header table row with first letter only in caps
# If header record, print header 
# Note that the last record is not processed properly because of EOF or something
# Print normal error message lines separated by | for wiki format
## replace {} with ""
## replace [] with ()
# Leaves other // comments in file - check for these
cat $1 | gawk 'BEGIN { 
FS="new KEYS"; 
RS="public static final class|public static final Action|Master"; 
EntityName = "";
ActionName = "";
KeyInfo[0] = ""; 
startout[0] = "";
entityout[0] = "";
endout[0] = "";
entityheader[0] = "";
entity_space_action[0] = "";
entity_for_users[0] = "";
entity_action_list = "input_files/entity_action_list.txt"
entity_list = "input_files/entity_list.txt"
} 
{  
   if ($0 ~ /\*/)
   { 
    next;
   }
   if (NF > 1)
   {   
      split ($1,EntityAction,"=");
      split (EntityAction[1],EntityActionNames," ");
      EntityName = EntityActionNames[1];
      gsub ("\<","",EntityName);
      gsub ("\>","",EntityName);
      ActionName = EntityActionNames[2];
      entity_space_action[NR] = EntityName " " ActionName;
      for (MyKey = 2;MyKey<5;MyKey ++)
      {
        if ($MyKey ~ "KEYS")
        {
          KeyInput = $MyKey;
          gsub("KEYS.","",KeyInput);
          gsub("\\[","",KeyInput);
          gsub("\]","",KeyInput);
          gsub("\{","",KeyInput);
          gsub("\}","",KeyInput);
          gsub("\);","",KeyInput);
          gsub("\n","",KeyInput);
          KeyInfo[MyKey] = KeyInput;
        } 
        else
        {
          KeyInfo[MyKey] = "";
        }     
      }
      KeyTotal = KeyInfo[2] KeyInfo[3] KeyInfo[4];
      split (KeyTotal,KeySplit,"\,|[ \t\n]+");
      keyHappy = "";
      for (KeyItem in KeySplit)
      {
        if (KeySplit[KeyItem] ~ /[A-Z][a-z]/)
        {
           if (keyHappy ~ /[A-Z][a-z]/)
           {
              keyHappy = keyHappy ", " KeySplit[KeyItem];
           }
           else  
           {
             keyHappy = KeySplit[KeyItem];
           } 
        }     
      }  
      startout[NR] = "| " ;
      endout[NR] =  " | " ActionName " | " keyHappy " |" ;
   }
 
   if (NF == 1)
   {
      eIndex = NR + 1;
      ENameHeading = $1;
      gsub ("\{","",ENameHeading);
      gsub ("\n","",ENameHeading);
      entityout[eIndex] = ENameHeading; 
      entity_for_users[NR] = ENameHeading;
      entityheader_fixcase = ENameHeading;
      gsub("_"," ",entityheader_fixcase);
      entityheader_fixcase = tolower(entityheader_fixcase);
      capital_letter = toupper(substr(entityheader_fixcase,1,2));
      rest_of_letters = substr(entityheader_fixcase,3);
      entityheader_for_sub = capital_letter rest_of_letters;   
      gsub ("ip","IP",entityheader_for_sub);
      gsub ("Ssl","SSL",entityheader_for_sub);
      gsub ("ldap","LDAP",entityheader_for_sub);
      entityheader[NR] = entityheader_for_sub;
   }      
}
      
END {
  print "|| Entity || Action || Additional Information ||";
  for (s=2; s<=NR-2; s++) 
  { 
    if (endout[s] !~ /[A-Z][a-z]/) 
      {
          print "|| h6. " entityheader[s] " || || ||" ;
          print entity_for_users[s] >> entity_list;
      }    
    else
      {
        print startout[s] entityout[s] endout[s];
        print entity_space_action[s] >> entity_action_list;
      }  
  }
}' >$2 
