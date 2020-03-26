#!/bin/zsh

#file_list=`ls -1d /Users/maryjane/Pictures/screenshots/v50 | grep "v50_" | grep "png" | grep -v "d_v50" | awk '{print $0}'`
directory="/Users/maryjane/Pictures/screenshots/v50/"

file_list=`ls -1 ${directory} | grep "v50_" | grep "png" | grep -v "dv50" | grep -v "d_v50" | awk '{print $0}'`

filearray=($file_list)

if [[ `echo ${filearray[*]}` == "" ]]; then
         print "Files not received"
else
 for ifile in `echo ${filearray[*]}`; do

        width=$(magick identify "${directory}$ifile" | awk -F "[ ]\|x" '{print $3}')
        height=$(magick identify "${directory}$ifile" | awk -F "[ ]\|x" '{print $4}')

        print "$ifile: ${width}x${height}"

        ifileout=$(print "d_${ifile}")   
#        print "$ifileout"

        convert "${directory}${ifile}" \
         -bordercolor gray75 -compose copy -border 3 \
         -bordercolor gray58 -compose copy -border 3 \
         -fuzz 50% -trim +repage "${directory}${ifileout}" 

        new_width=$(magick identify "${directory}$ifileout" | awk -F "[ ]\|x" '{print $3}')
        new_height=$(magick identify "${directory}$ifileout" | awk -F "[ ]\|x" '{print $4}')

        change_width=$(( width - new_width ))
        print "changewidth: $change_width"

        if [[ change_width -ge 20 ]]; then
            cp ${directory}$ifile ${directory}$ifileout
        else
            if [[ change_width -eq 1 ]]; then
                convert "$directory${ifile}" -crop "${new_width}x${new_height}+0+0" +repage \
                -bordercolor gray75 -compose copy -border 3 \
                -bordercolor gray58 -compose copy -border 3 \
                -fuzz 50% -trim +repage \
                -fuzz 50% -trim +repage "$directory${ifileout}" 
            else    
                convert "${directory}${ifile}" \
                -bordercolor gray75 -compose copy -border 3 \
                -bordercolor gray58 -compose copy -border 3 \
                -fuzz 50% -trim +repage \
                -fuzz 50% -trim +repage "${directory}${ifileout}" 
            fi
        fi    

        print "Processed file ${ifileout}" 
 done
fi