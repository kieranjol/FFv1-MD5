# Written by Kieran O'Leary, with a major review and overhaul/cleanup by Zach Kelling aka @Zeekay

import subprocess
import sys
import filecmp
from glob import glob
import os

# Directory with files that we want to transcode losslessly and generate metadata for
video_dir = sys.argv[1]

# Change directory to directory with video files
wd = os.path.dirname(video_dir)
os.chdir(wd)

# Find all video files to transcode
video_files =  glob('*.mov') + glob('*.mp4')



for filename in video_files: #Begin a loop for all .mov and .mp4 files.

	# Assigning variable names to the new files we're going to create.
	inputxml  = filename + ".xml"	
	output    = filename + ".mkv"
	outputxml = output + ".xml"
	fmd5      = filename + ".framemd5"
	fmd5ffv1  = output + ".framemd5"

	# Transcode video file writing frame md5 and output appropriately

	subprocess.call(['ffmpeg',
			'-i', filename, 
			'-c:v', 'ffv1', 		# Use FFv1 codec
			'-g','1',			# Use intra-frame only aka ALL-I aka GOP=1
			'-level','3',			# Use Version 3 of FFv1
			'-c:a','copy',			# Copy and paste audio bitsream with no transcoding
			output,	
			'-f','framemd5','-an'		# Create decoded md5 checksums for every frame of the input. -an ignores audio
			, fmd5 ])
	subprocess.call(['ffmpeg',			# Create decoded md5 checksums for every frame of the ffv1 output
			'-i',output,
			'-f','framemd5','-an',
			fmd5ffv1 ])
	
	# Verify that the video really is lossless by comparing the fixity of the two framemd5 files. 
	if filecmp.cmp(fmd5, fmd5ffv1, shallow=False): 
		print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"
	else:
		print "YOUR CHECKSUMS DO NOT MATCH, BACK TO THE DRAWING BOARD!!!"
		sys.exit()				# Script will exit the loop if transcode is not lossless.


	# Write metadata for original video file - with open will auto close the file.
	with open(inputxml, "w+") as fo:
		mediaxmlinput = subprocess.check_output(['mediainfo',
						'-f',
						'--language=raw', # Use verbose output.
						'--output=XML',
						filename ])
		fo.write(mediaxmlinput)
	

	# Write metadata for output video file
	with open(outputxml, "w+") as fo:
		mediaxmloutput = subprocess.check_output(['mediainfo',
						'-f',
						'--language=raw',
						'--output=XML',
						output ])
		fo.write(mediaxmloutput)
	
	inmagicxml = outputxml + ".xml"
	vcodec = subprocess.check_output(['xml','sel', '-t', '-m', "Mediainfo/File/track[@type='Video']", '-v', 'Codec', outputxml ])
	width = subprocess.check_output(['xml','sel', '-t', '-m', "Mediainfo/File/track[@type='Video']", '-v', 'Width', outputxml ])
	height = subprocess.check_output(['xml','sel', '-t', '-m', "Mediainfo/File/track[@type='Video']", '-v', 'Height', outputxml ])
	DAR = subprocess.check_output(['xml','sel', '-t', '-m', "Mediainfo/File/track[@type='Video']", '-v', 'DisplayAspectRatio', outputxml ])

	acodec = subprocess.check_output(['xml','sel', '-t', '-m', "Mediainfo/File/track[@type='Audio']", '-v', 'Codec', outputxml ])

	duration = subprocess.check_output(['xml','sel', '-t', '-m', "Mediainfo/File/track[@type='General']", '-v', 'Duration_String4', outputxml ])
	wrapper = subprocess.check_output(['xml','sel', '-t', '-m', "Mediainfo/File/track[@type='General']", '-v', 'FileExtension', outputxml ])
	filesize = subprocess.check_output(['xml','sel', '-t', '-m', "Mediainfo/File/track[@type='General']", '-v', 'FileSize_String4', outputxml ])




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
			
		

		
