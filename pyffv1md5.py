import subprocess
import sys
filename = sys.argv[1]
#http://bytes.com/topic/python/answers/649282-how-add-extension-input-filename
output = filename + ".mkv"
fmd5 = filename + ".framemd5"
fmd5ffv1 = output + ".framemd5"
print filename
print output

#Convert video to lossless ffv1 and generate md5 checksums for every frame
subprocess.call(['ffmpeg','-i', filename, '-c:v', 'ffv1','-g','1','-level','3', '-c:a','copy', output, '-f','framemd5','-an', fmd5 ])
subprocess.call(['ffmpeg','-i', output, '-f','framemd5','-an', fmd5ffv1 ])
print fmd5
print fmd5ffv1
#http://bioportal.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/filecmp/index.html and https://docs.python.org/2/library/filecmp.html

#compare the two checksum files
if filecmp.cmp(fmd5, fmd5ffv1, shallow=False): 
	print "YOUR FILES ARE LOSSLESS YOU SHOULD BE SO HAPPY!!!"
else:
	print "YOUR CHECKSUMS DO NOT MATCH, BACK TO THE DRAWING BOARD!!!"

#Next section creates mediainfo xml output for source and output. #reference#http://www.tutorialspoint.com/python/python_files_io.htm

fo = open(inputxml, "w+")
mediaxmlinput = subprocess.check_output(['mediainfo','-f','--language=raw','--output=XML', filename ])
fo.write(mediaxmlinput)
fo.close

fo = open(outputxml, "w+")
mediaxmloutput = subprocess.check_output(['mediainfo','-f','--language=raw','--output=XML', output ])
fo.write(mediaxmloutput)
fo.close
