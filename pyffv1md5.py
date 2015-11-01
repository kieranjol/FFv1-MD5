import subprocess
import sys
import filecmp
import glob
import os

wd = os.path.dirname(os.path.realpath(sys.argv[1]))
os.chdir(wd)
filelist =  glob.glob('*.mov')
#this seems to append another argument to glob, which usually
#takes one argument. may not be good code?
filelist +=  glob.glob('*.mp4')
filename = sys.argv[1]

for filename in filelist:

	inputxml = filename + ".xml"
	#http://bytes.com/topic/python/answers/649282-how-add-extension-input-filename
	output = filename + ".mkv"
	outputxml = output + ".xml"
	fmd5 = filename + ".framemd5"
	fmd5ffv1 = output + ".framemd5"

	subprocess.call(['ffmpeg',
			'-i', filename, 
			'-c:v', 'ffv1',
			'-g','1',
			'-level','3',
			'-c:a','copy',
			output,
			'-f','framemd5','-an'
			, fmd5 ])
	subprocess.call(['ffmpeg',
			'-i',output,
			'-f','framemd5','-an',
			fmd5ffv1 ])
	
	if filecmp.cmp(fmd5, fmd5ffv1, shallow=False):
		print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"
	else:
		print "YOUR CHECKSUMS DO NOT MATCH, BACK TO THE DRAWING BOARD!!!"
		sys.exit()


	#http://www.tutorialspoint.com/python/python_files_io.htm
	fo = open(inputxml, "w+")
	mediaxmlinput = subprocess.check_output(['mediainfo',
						'-f',
						'--language=raw',
						'--output=XML',
						filename ])
	fo.write(mediaxmlinput)
	fo.close

	fo = open(outputxml, "w+")
	mediaxmloutput = subprocess.check_output(['mediainfo',
						'-f',
						'--language=raw',
						'--output=XML',
						output ])
	fo.write(mediaxmloutput)
	fo.close

		
