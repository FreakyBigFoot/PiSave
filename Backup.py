#!/usr/bin/python
import re, os, dropbox, time
from dropbox.files import WriteMode

#This Is Your Unique Key Given By Dropbox
dbx = dropbox.Dropbox('API_KEY')

#This Forces Dropbox To Overwrite Any Exisitng Saves When Running This Script
overwrite = WriteMode('overwrite', None)

CHUNK_SIZE = 4 * 1024 * 1024

#Add File Types You'd Like To Backup Here
filetypes = ('\.state*|\.srm*|\.dat*|\.nv*|\.hi*|\.hs*|\.cfg*|\.fs*|\.eep*')

num = 0
numdone = 0
for root, dirs, files in os.walk(r'/home/pi/RetroPie/roms'):
    for saves in files:
        #if saves.endswith(filetypes):
        if re.search(filetypes, saves):
            num += 1
        
print str(num) + ' Saves Found'

for root, dirs, files in os.walk(r'/home/pi/RetroPie/roms'):
    for saves in files:
        file_path = root + '/' + saves
        dest_path = root + '/' + saves
        #if saves.endswith(filetypes):
        if re.search(filetypes, saves):              
            f = open(file_path)
            file_size = os.path.getsize(file_path)
            if file_size <= CHUNK_SIZE:
            
                dbx.files_upload(f.read(), dest_path, overwrite)
                numdone += 1
                print str(numdone) + '/' + str(num) + ' saves uploaded'
                
            else:

                upload_session_start_result = dbx.files_upload_session_start(f.read(CHUNK_SIZE))
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=f.tell())
                commit = dropbox.files.CommitInfo(path=dest_path)

                while f.tell() < file_size:
                    if ((file_size - f.tell()) <= CHUNK_SIZE):
                        dbx.files_upload_session_finish(f.read(CHUNK_SIZE),
                                                        cursor,
                                                        commit)
                        numdone += 1
                        print str(numdone) + '/' + str(num) + ' saves uploaded'
                    else:
                        dbx.files_upload_session_append(f.read(CHUNK_SIZE),
                                                        cursor.session_id,
                                                        cursor.offset)
                        cursor.offset = f.tell()
                        numdone += 1
                        print str(numdone) + '/' + str(num) + ' saves uploaded'
            f.close()
            time.sleep(2)
