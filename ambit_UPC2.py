# -*- coding: utf-8 -*-

import os;
import re;
import sys;
import subprocess;
from time import gmtime, strftime
import traceback
import shutil

kms_list = [('\\\\192.168.11.213\\KMStorage\\UPC\\471\\275', '666', '667')]
kms_list = [('\\\\192.168.11.213\\KMStorage', 'UPC')]
convert_tool =  "C:\\Program Files\\ImageMagick-7.0.2-Q16\\convert.exe "
ffmpeg_tool = "C:\\app\\ffmpeg.exe "
mediainfo_tool = 'C:\\app\\mediainfo_CLI_0.7.87\\mediainfo.exe -f '
f_pic = 300
t_pic = 150
t_size = 15000 # 15K

regex_mediainfo_last_modification = r"File last modification date\s+:\s+(.+)$"
regex_mediainfo_width = "Width\s+:\s+(\d+)$"
regex_mediainfo_height = "Height\s+:\s+(\d+)$"
regex_mediainfo_size = "File size\s+:\s+(\d+)$"
regex_pic_format = "^(\S+)\.(jpg|png|jpeg)$"
regex_pic_ft_format = "^(\S+)_(f|t)\.(jpg|png|jpeg)$"
regex_folder_reg = "KMStorage\\\\UPC\\\\\S{3}\\\\\S{3}\\\\\S{3}\\\\\S{3,5}\\\\(\S+)$"

pattern_mediainfo_last_modification = re.compile(regex_mediainfo_last_modification, re.IGNORECASE)
pattern_mediainfo_width = re.compile(regex_mediainfo_width, re.IGNORECASE)
pattern_mediainfo_height = re.compile(regex_mediainfo_height, re.IGNORECASE)
pattern_mediainfo_size = re.compile(regex_mediainfo_size, re.IGNORECASE)
pattern_pic_format = re.compile(regex_pic_format, re.IGNORECASE)
pattern_pic_ft_format = re.compile(regex_pic_ft_format, re.IGNORECASE)
pattern_folder_reg = re.compile(regex_folder_reg, re.IGNORECASE)

class MediaInfo:
    def __init__(self):
        self.h = 0
        self.w = 0
        self.size = 0
        self.last_modification = 'NA'
        self.file = ''
    def set_all(self, h, w, size, last_mod):
        self.h = h
        self.w = w
        self.size = size
        self.last_modification = last_mod
    def set_f(self, file):
        self.__init__()
        self.file = file
    def w_h_size(self):
        return(str(self.w) + 'x' + str(self.h) + ':' + str(self.size))

def run_mediainfo(MediaInfo):
    exec_cmd = '{0} {1}'.format(mediainfo_tool, MediaInfo.file).split()
    run_command2(exec_cmd, MediaInfo)
        
def run_command2(command, tmp_MediaInfo):
    o_w = o_h = o_size = 0
    last_mod = 'NA'
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, b''):
        chg_line = line.rstrip().decode('utf-8')
        m_wav = pattern_mediainfo_last_modification.search(chg_line)
        if m_wav is not None:
            last_mod = m_wav.group(1)
        else:
            m_wav = pattern_mediainfo_width.search(chg_line)
            if m_wav is not None:
                o_w = m_wav.group(1)
            else:
                m_wav = pattern_mediainfo_height.search(chg_line)
                if m_wav is not None:
                    o_h = m_wav.group(1)
                else:
                    m_wav = pattern_mediainfo_size.search(chg_line)
                    if m_wav is not None:
                        o_size = m_wav.group(1)
    if (p and p.stdout):
        p.stdout.close()
    if (p and p.stderr):
        p.stderr.close()
    tmp_MediaInfo.set_all(o_h, o_w, o_size, last_mod)
    return 

def check_remove(full_file_path):
    if os.path.isfile(full_file_path):
        os.remove(full_file_path)
    
def traverse_dir(km_folder, outfile1, outfile2, outfile3, outfile4):
    org_MediaInfo = MediaInfo()
    new_f_MediaInfo = MediaInfo()
    org_f_MediaInfo = MediaInfo()
    new_t_MediaInfo = MediaInfo()
    org_t_MediaInfo = MediaInfo()
    
    with open(outfile1, 'w', encoding='utf-8') as okfp, open(outfile2, 'w',encoding='utf-8') as failfp, open(outfile3, 'w',encoding='utf-8') as logfp, open(outfile4, 'w',encoding='utf-8') as tranfp:
        for root, dirs, files in os.walk(km_folder, topdown=False):
            logfp.write(strftime("%Y-%m-%d %H:%M:%S") + ' folder ' + root + '\n')
            m1 = pattern_folder_reg.search(root)
            if not m1:
                logfp.write('\tskip\n')
                continue
            for name in sorted(files):
                m2 = pattern_pic_format.search(name)
                chkfile = root + '\\' + name
                if m2:
                    isrc = str(m2.group(1))
                    pic_tail = m2.group(2)
                    org_f_file = root + '\\org_' + isrc + '_f.' + pic_tail
                    org_t_file = root + '\\org_' + isrc + '_t.' + pic_tail
                    check_remove(org_f_file)
                    check_remove(org_t_file)

                    f_file = root + '\\' + isrc + '_f.' + pic_tail
                    t_file = root + '\\' + isrc + '_t.' + pic_tail
                    new_f_file = root + '\\new_' + isrc + '_f.' + pic_tail
                    new_t_file = root + '\\new_' + isrc + '_t.' + pic_tail
                    org_MediaInfo.set_f(chkfile)
                    org_f_MediaInfo.set_f(f_file)
                    org_t_MediaInfo.set_f(t_file)
                    new_f_MediaInfo.set_f(new_f_file)
                    new_t_MediaInfo.set_f(new_t_file)
                    check_remove(new_f_file)
                    check_remove(new_t_file)
                    
                    if os.path.isfile(chkfile):
                        run_mediainfo(org_MediaInfo)

                    if os.path.isfile(f_file) and os.path.isfile(t_file):
                        logfp.write('Processing ' + chkfile + '...\n')
                        is_fail1 = is_fail2 = 0
                        run_mediainfo(org_f_MediaInfo)
                        run_mediainfo(org_t_MediaInfo)
                        short_msg = org_MediaInfo.w_h_size() + ', ' + org_f_MediaInfo.w_h_size() + ', ' + org_t_MediaInfo.w_h_size() + ', ' + org_MediaInfo.last_modification + ', ' + org_f_MediaInfo.last_modification + ', ' + org_t_MediaInfo.last_modification
                        if ((org_MediaInfo.h == 0) or (org_MediaInfo.w == 0)):
                            logfp.write(' FAIL, ' + short_msg + '\n')
                            failfp.write(chkfile + ', ' + short_msg + '\n')
                            continue

                        if ((int(org_f_MediaInfo.h) > f_pic) or (int(org_f_MediaInfo.w) > f_pic)):
                            is_fail1 = 1
                            os.system('\"{0}\" {1} -resize {2}x{2} -quality 50 {3}'.format(convert_tool, chkfile, f_pic, new_f_file))
                            run_mediainfo(new_f_MediaInfo)
                            if (((int(new_f_MediaInfo.h) - f_pic) < 2) and ((int(new_f_MediaInfo.w) - f_pic) < 2)):
                                try:
                                    check_remove(f_file)
                                    shutil.move(new_f_file, f_file)
                                    run_mediainfo(org_f_MediaInfo)
                                    is_fail1 = 2
                                except:
                                    print("\n".format(f_file))
                                    print("Unexpected error: {}\n".format(sys.exc_info()))
                                    print("Unexpected error: {}\n".format(traceback.format_list(traceback.extract_tb(sys.exc_info()[2]))))

                        if ((int(org_t_MediaInfo.h) > t_pic) or (int(org_t_MediaInfo.w) > t_pic)):
                            is_fail2 = 1
                            os.system('\"{0}\" {1} -resize {2}x{2} -quality 50 {3}'.format(convert_tool, chkfile, t_pic, new_t_file))
                            run_mediainfo(new_t_MediaInfo)
                            if (((int(new_t_MediaInfo.h) - t_pic) < 1) and ((int(new_t_MediaInfo.w) - t_pic) < 1)):
                                try:
                                    check_remove(t_file)
                                    shutil.move(new_t_file, t_file)
                                    run_mediainfo(org_t_MediaInfo)
                                    is_fail2 = 2
                                except:
                                    print("\n".format(t_file))
                                    print("Unexpected error: {}\n".format(sys.exc_info()))
                                    print("Unexpected error: {}\n".format(traceback.format_list(traceback.extract_tb(sys.exc_info()[2]))))

                        if ((int(org_t_MediaInfo.size) > t_size)):
                            os.system('{0} -loglevel 0 -i {1} -q:v 5 -vf scale=\"\'if(gt(a,1/1),{2},-1)\':\'if(gt(a,1/1),-1,{2})\'\" -y {3}'.format(ffmpeg_tool, chkfile, f_pic, new_f_file))
                            run_mediainfo(new_f_MediaInfo)
                            if (int(new_f_MediaInfo.size) < int(org_f_MediaInfo.size)):
                                try:
                                    check_remove(f_file)
                                    shutil.move(new_f_file, f_file)
                                    is_fail1 = 3
                                except:
                                    print("\n".format(f_file))
                                    print("Unexpected error: {}\n".format(sys.exc_info()))
                                    print("Unexpected error: {}\n".format(traceback.format_list(traceback.extract_tb(sys.exc_info()[2]))))
                            
                            os.system('{0} -loglevel 0 -i {1} -q:v 5 -vf scale=\"\'if(gt(a,1/1),{2},-1)\':\'if(gt(a,1/1),-1,{2})\'\" -y {3}'.format(ffmpeg_tool, chkfile, t_pic, new_t_file))
                            run_mediainfo(new_t_MediaInfo)
                            if (int(new_t_MediaInfo.size) < int(org_t_MediaInfo.size)):
                                try:
                                    check_remove(t_file)
                                    shutil.move(new_t_file, t_file)
                                    is_fail2 = 3
                                except:
                                    print("\n".format(t_file))
                                    print("Unexpected error: {}\n".format(sys.exc_info()))
                                    print("Unexpected error: {}\n".format(traceback.format_list(traceback.extract_tb(sys.exc_info()[2]))))

                        check_remove(new_f_file)
                        check_remove(new_t_file)
                        long_msg = short_msg + ', ' + new_f_MediaInfo.w_h_size() + ', ' + new_t_MediaInfo.w_h_size() + ', ' + new_f_MediaInfo.last_modification + ', ' + new_t_MediaInfo.last_modification + '\n'

                        if  ((is_fail1 == 3) or (is_fail2 == 3)):
                            logfp.write(' TRANS2, ' + long_msg)
                            tranfp.write(chkfile + ',2, ' + long_msg)
                                    
                        if  ((is_fail1 == 2) or (is_fail2 == 2)):
                            logfp.write(' TRANS, ' + long_msg)
                            tranfp.write(chkfile + ',1, ' + long_msg)
                                    
                        if  ((is_fail1 == 1) or (is_fail2 == 1)):
                            logfp.write(' FAIL, ' + short_msg + '\n')
                            failfp.write(chkfile + ', ' + short_msg + '\n')
                                
                        if  ((is_fail1 ==0) and (is_fail2 ==0)):
                            logfp.write(' OK, ' + short_msg + '\n')
                            okfp.write(chkfile + ', ' + short_msg + '\n')
                    else:
                        m2 = pattern_pic_ft_format.search(name)
                        if (m2 is None):
                            short_msg = org_MediaInfo.w_h_size() + ', ' + org_MediaInfo.last_modification
                            logfp.write('\tskip ' + chkfile + ' : No f and t ' + short_msg + '\n')
                            failfp.write('\tskip ' + chkfile + ' : No f and t ' + short_msg + '\n')
                else:
                    m2 = pattern_pic_ft_format.search(name)
                    if ((m2 is None) and (name != "Thumbs.db")):
                        logfp.write('Wrong file name pattern: ' + chkfile + '\n')
                        failfp.write(chkfile + ' ,Wrong file name pattern\n')

if __name__== '__main__':    
    for kms_list_index in range(len(kms_list)):
        #print(str(kms_list_index), kms_list[kms_list_index],str(len(kms_list[kms_list_index])))
        for kms_list_tup in range(1,len(kms_list[kms_list_index])):
            km_dir = kms_list[kms_list_index][0] + '\\' + kms_list[kms_list_index][kms_list_tup]
            ofile1 = 'Ok_' + str(kms_list_index) + '_' + kms_list[kms_list_index][kms_list_tup] + '.txt'
            ofile2 = 'Fail_' + str(kms_list_index) + '_' + kms_list[kms_list_index][kms_list_tup] + '.txt'
            ofile3 = 'Log_' + str(kms_list_index) + '_' + kms_list[kms_list_index][kms_list_tup] + '.txt'
            ofile4 = 'Tran_' + str(kms_list_index) + '_' + kms_list[kms_list_index][kms_list_tup] + '.txt'
            traverse_dir(km_dir, ofile1, ofile2, ofile3, ofile4)    