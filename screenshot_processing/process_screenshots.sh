#!/bin/zsh

#file_list=`ls -1d /Users/maryjane/Pictures/screenshots/v50 | grep "v50_" | grep "png" | grep -v "d_v50" | awk '{print $0}'`

file_list=`ls -1 /Users/maryjane/Pictures/screenshots/v50/ | grep "v50_" | grep "png" | grep -v "dv50" | grep -v "d_v50" | awk '{print $0}'`

filearray=($file_list)

if [[ `echo ${filearray[*]}` == "" ]]; then
         print "files not received"
else
 for ifile in `echo ${filearray[*]}`; do

        width=$(magick identify "$ifile" | awk -F "[ ]\|x" '{print $3}')
        height=$(magick identify "$ifile" | awk -F "[ ]\|x" '{print $4}')

        print "$ifile: ${width}x${height}"

        ifileout=$(print "d_${ifile}")   
#        print "$ifileout"

        convert "${ifile}" \
         -bordercolor gray75 -compose copy -border 3 \
         -bordercolor gray58 -compose copy -border 3 \
         -fuzz 50% -trim +repage "${ifileout}" 

        new_width=$(magick identify "$ifileout" | awk -F "[ ]\|x" '{print $3}')
        new_height=$(magick identify "$ifileout" | awk -F "[ ]\|x" '{print $4}')

        change_width=$(( width - new_width ))
        print "changewidth: $change_width"

        if [[ change_width -ge 200 ]]; then
            cp $ifile $ifileout
        else
            convert "${ifile}" \
            -bordercolor gray75 -compose copy -border 3 \
            -bordercolor gray58 -compose copy -border 3 \
            -fuzz 50% -trim +repage \
            -fuzz 50% -trim +repage "${ifileout}" 
            
        fi    

        print "Processed file ${ifileout}" 
 done
fi

#         
