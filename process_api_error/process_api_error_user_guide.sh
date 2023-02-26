#! /bin/sh
# Convert APIError.java to Confluence Wiki Format
#
# Version for User Guide with only Message ID and Message Text
#
# Read APIError.java file $1 and write to wiki output $2
#
# Cut the java code from the beginning and end of the APIError.java because it is not processed by this script
# Also cut the first section of error codes as that is not process either
#
# Mark comments as header records
# Strip whitespace in the file
# Set the record separator as "), "
# Print the first field of lines with one field beginning with // as h5. in wiki format after stripping non-numerics, then print header table row with first letter only in caps
# If header record, print header 
# If leftover piece message record (created by record separator "), " problem, print it in a message box on a new line
# Note that the last record isn't processed properly because of EOF
# Print normal error message lines separated by | for wiki format
## replace {} with ""
## replace [] with ()
# Leaves end of line comments in file - these should be checked and deleted by hand!
# 
cat $1 | gawk '
{
   if ($0 ~ /^ *\/\//)  
      { print "h5. " $0 "\")," ; } 
   else 
      { print $0 }
}' | sed ':a;N;$!ba;s/^[ \t]*/ /;s/[ \t]*$/ /;' | sed 's/^ *//;s/ *$//;s/ \{1,\}/ /g' | sed ':a;N;$!ba;s/\n//g'  \
| gawk 'BEGIN { FS="\", *\"|\\(\""; RS="\"\)\\,|\)\\, +"; } 
{ 

   if (NF > 1)
   {
      message_label[NR] = $1;
      message_id[NR] = $2;
      message_txt[NR] = $3;
      i = 3; 
      while (i<NF)
         { message_txt[NR] = message_txt[NR] $i ; i++ }
      g = message_txt[NR];
      gsub(/\{/,"",g); gsub(/\}/,"",g); gsub(/\[/,"(",g); gsub(/\]/,")",g); gsub(/(\")( *)(\+)( *)(\")/," ",g); gsub(/\" *\+/," ",g); 
      message_txt[NR] = g;
      output_line [NR] = "| " message_id[NR] " | " message_txt[NR] " |";
   }
 
   if (NF == 1)
   {
      if ($0 ~ /(^h5\.) *\/\//)
      { 
         h = $0;
         gsub(/(^h5\.) *\/\//,"",h);
         l = length(h);
         header_start = substr(h,1,2);
         header_end = substr(h,3);
         header_first = toupper(header_start);   
         header_rem = tolower(header_end);
         header_comp = (header_first header_rem);
         output_line [NR] = "\nh5. " header_comp "\n|| Internal Message ID {color:#efefef}__________________{color}|| Message {color:#efefef}____________________________________________________________{color} ||"; 
      }
      else
      { 
      if ($0 !~ /^*$/)
         { 
              concat_msg_txt = message_txt[NR-1] "), " $0; 
              output_line[NR-1] = "| " message_id[NR-1] " | " concat_msg_txt " |" ;
              output_line[NR] = "NOPRINT";
              next;
         }
      }      
   }
}
      
END {for (s=1; s<=NR; s++) {if (output_line[s] !~ "NOPRINT") {print output_line[s];}}}' >$2 
