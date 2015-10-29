import subprocess
import sys
filename = sys.argv[1]
#http://bytes.com/topic/python/answers/649282-how-add-extension-input-filename
output = filename + ".mkv"
fmd5 = filename + ".framemd5"
fmd5ffv1 = output + ".framemd5"
print filename
print output


subprocess.call(['ffmpeg','-i', filename, '-c:v', 'ffv1','-g','1','-level','3', '-c:a','copy', output, '-f','framemd5','-an', fmd5 ])
subprocess.call(['ffmpeg','-i', output, '-f','framemd5','-an', fmd5ffv1 ])
