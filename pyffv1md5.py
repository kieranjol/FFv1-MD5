# Written by Kieran O'Leary, with a major review and overhaul/cleanup by Zach Kelling aka @Zeekay

import subprocess
import sys
import filecmp
from glob import glob
import os
from Tkinter import *
import tkFileDialog
root = Tk()

# Create file-open dialog.
root.update()
# Directory with files that we want to transcode losslessly and generate metadata for
video_dir = tkFileDialog.askopenfilename(parent=root)

# Change directory to directory with video files
wd = os.path.dirname(video_dir)
os.chdir(wd)

# Find all video files to transcode
video_files =  glob('*.mov') + glob('*.mp4')

for filename in video_files: #Begin a loop for all .mov and .mp4 files.

    # Generate new directory names in AIP
    metadata_dir   = wd + "/%s/metadata" % os.path.splitext(filename)[0]
    data_dir   = wd + "/%s/data" % os.path.splitext(filename)[0]
    provenance_dir   = wd + "/%s/provenance" % os.path.splitext(filename)[0]
    
    # Actually create the directories.
    os.makedirs(metadata_dir)
    os.makedirs(data_dir)
    os.makedirs(provenance_dir)
    
    #Generate filenames for new files in AIP.
    inputxml  = "%s/%s.xml" % (metadata_dir, filename)
    output    = "%s/%s.mkv" % (data_dir, os.path.splitext(filename)[0])
    
    # Generate filename of ffv1.mkv without the path.
    outputfilename = os.path.basename(output)
    
    outputxml = "%s/%s.xml" % (metadata_dir, outputfilename)
    fmd5      = "%s/%s.framemd5" % (provenance_dir, filename)
    fmd5ffv1  = output + ".framemd5"
	
    # Transcode video file writing frame md5 and output appropriately
    subprocess.call(['ffmpeg',
                    '-i', filename, 
                    '-c:v', 'ffv1',        # Use FFv1 codec
                    '-g','1',              # Use intra-frame only aka ALL-I aka GOP=1
                    '-level','3',          # Use Version 3 of FFv1
                    '-c:a','copy',         # Copy and paste audio bitsream with no transcoding
                    '-map','0',
                    '-dn',
                    output,	
                    '-f','framemd5','-an'  # Create decoded md5 checksums for every frame of the input. -an ignores audio
                    , fmd5 ])
    subprocess.call(['ffmpeg',     # Create decoded md5 checksums for every frame of the ffv1 output
                    '-i',output,
                    '-f','framemd5','-an',
                    fmd5ffv1 ])
	
	# Verify that the video really is lossless by comparing the fixity of the two framemd5 files. 
    if filecmp.cmp(fmd5, fmd5ffv1, shallow=False): 
		print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"
    else:
		print "YOUR CHECKSUMS DO NOT MATCH, BACK TO THE DRAWING BOARD!!!"
		sys.exit()                 # Script will exit the loop if transcode is not lossless.


	# Write metadata for original video file - with open will auto close the file.
    with open(inputxml, "w+") as fo:
		mediaxmlinput = subprocess.check_output(['mediainfo',
							'-f',
							'--language=raw', # Use verbose output.
							'--output=XML',
							filename ])       #input filename
		fo.write(mediaxmlinput)
	

	# Write metadata for output video file
    with open(outputxml, "w+") as fo:
		mediaxmloutput = subprocess.check_output(['mediainfo',
							'-f',
							'--language=raw',
							'--output=XML',
							output ])         #output ffv1 file
		fo.write(mediaxmloutput)
	
	# Ok so initially i was chopping up the mediainfo xml, now I'm slowly moving towards extracting the info directly from the video via MI. WORK IN PROGRESSSSSS!!!.
    inmagicxml = outputxml + ".xml"
    vcodec = subprocess.check_output(['xml','sel', '-t', '-m',
					"Mediainfo/File/track[@type='Video']", '-v', 'Codec', 
					outputxml ])
    width = subprocess.check_output(['xml','sel', '-t', '-m', 
					"Mediainfo/File/track[@type='Video']", '-v', 'Width', 
					outputxml ])
    
    height = subprocess.check_output(['MediaInfo', '--Language=raw', '--Full', '--inform=Video;%Height%', output ]).replace('\n', '')
  
    DAR = subprocess.check_output(['xml','sel', '-t', '-m',
					"Mediainfo/File/track[@type='Video']", '-v', 'DisplayAspectRatio', 
					outputxml ])
    #Multiple possible values, so newline is used, then only first line is extracted.
    acodec = subprocess.check_output(['MediaInfo', '--Language=raw', '--Full', '--inform=Audio;%Codec%\\n', output ]).split('\n', 1)[0].replace('\n', '')                    # Only taking info from the first stream for now.

    duration = subprocess.check_output(['MediaInfo', '--Language=raw', '--Full', '--inform=General;%Duration_String4%', output ]).replace('\n', '')
 
 
    wrapper = subprocess.check_output(['MediaInfo', '--Language=raw', '--Full', '--inform=General;%FileExtension%', output ]).replace('\n', '')
    
    filesize = subprocess.check_output(['xml','sel', '-t', '-m', 
					"Mediainfo/File/track[@type='General']", '-v', 'FileSize_String4',
					outputxml ])

	#Writes an inmagic DBTextworks compliant xml file usin ght values from the previous section.
    with open(inmagicxml, "w+") as fo:
		fo.write('<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>\n')
		fo.write('<inm:Results productTitle="Inmagic DB/TextWorks for SQL" productVersion="13.00" xmlns:inm="http://www.inmagic.com/webpublisher/query">\n')
		fo.write('<inm:Recordset setCount="1">\n')
		fo.write('<inm:Record setEntry="0">\n')	
		fo.write('<inm:Video-codec>%s</inm:Video-codec>\n' % vcodec) 
		fo.write('<inm:D-Audio-codec>%s</inm:D-Audio-codec>\n' % acodec)
		fo.write('<inm:D-Duration>%s</inm:D-Duration>\n' % duration)
		fo.write('<inm:D-video-width >%s</inm:D-video-width >\n' % width)
		fo.write('<inm:D-video-height >%s</inm:D-video-height >\n' % height)
		fo.write('<inm:Display-Aspect-ratio >%s</inm:Display-Aspect-ratio >\n' % DAR)
		fo.write('<inm:Wrapper>%s</inm:Wrapper>\n' % wrapper)
		fo.write('<inm:D-File-Size >%s</inm:D-File-Size >\n' % filesize)
		fo.write('</inm:Record>\n')	
		fo.write('</inm:Recordset>\n')	
		fo.write('</inm:Results>\n')	
    

		
