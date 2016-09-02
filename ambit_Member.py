# -*- coding: utf-8 -*-

import os;
import re;
import sys;
import subprocess;
from time import gmtime, strftime
import traceback
import shutil

kms_list = [('\\\\192.168.11.213\\KMStorage\\HeartMusicMember', 'FILE')]
convert_tool =  "C:\\Program Files\\ImageMagick-7.0.2-Q16\\convert.exe "
ffmpeg_tool = "C:\\app\\ffmpeg.exe "
mediainfo_tool = 'C:\\app\\mediainfo_CLI_0.7.87\\mediainfo.exe -f '
f_pic = 170
o_w=o_h=o_size=0
i = 2
t_size = 15000 # 15K
last_mod = ''

def check_remove(full_file_path):
    if os.path.isfile(full_file_path):
        os.remove(full_file_path)    

def run_command(command):
    global o_h,o_w,o_size,last_mod
    o_w=o_h=o_size=0
    last_mod = 'NA'
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    for line in iter(p.stdout.readline, b''):
        chg_line = line.rstrip().decode('utf-8')
        m_wav = re.match('File last modification date\s+:\s+(.+)$', chg_line)
        if m_wav:
            last_mod = m_wav.group(1)
        m_wav = re.match('Width\s+:\s+(\d+)$', chg_line)
        if m_wav:
            o_w = m_wav.group(1)
        m_wav = re.match('Height\s+:\s+(\d+)$', chg_line)
        if m_wav:
            o_h = m_wav.group(1)
        m_wav = re.match('File size\s+:\s+(\d+)$', chg_line)
        if m_wav:
            o_size = m_wav.group(1)
    if (p and p.stdout):
        p.stdout.close()
    if (p and p.stderr):
        p.stderr.close()
    return (o_h, o_w, last_mod, o_size)

def traverse_dir(km_folder, outfile1, outfile2, outfile3, outfile4):
    global i
    with open(outfile1, 'w', encoding='utf-8') as okfp, open(outfile2, 'w',encoding='utf-8') as failfp, open(outfile3, 'w',encoding='utf-8') as logfp, open(outfile4, 'w',encoding='utf-8') as tranfp:
        for root, dirs, files in os.walk(km_folder, topdown=False):
            logfp.write(strftime("%Y-%m-%d %H:%M:%S") + ' checking folder ' + root + '\n')
            m1 = re.search('KMStorage\\\\HeartMusicMember\\\\FILE$' , root, re.IGNORECASE)
            if not m1:
                logfp.write('\tskip\n')
                continue
            for name in sorted(files):
                chkfile = root + '\\' + name
                m2 = re.match('^(\d+)\.(jpg|png|jpeg)$', name, re.IGNORECASE)
                if m2:
                    isrc = m2.group(1)
                    pic_tail = m2.group(2)
                    if os.path.isfile(chkfile):
                        logfp.write('Processing ' + chkfile + '...\n')
                        is_fail = 0
                        org_w = 0
                        org_h = 0
                        org_size = 0
                        org_last_mod = ''
                        fnew_w = 0
                        fnew_h = 0
                        fnew_size = 0
                        new_f_last_mod = ''
                        ffnew_w = 0
                        ffnew_h = 0
                        ffnew_size = 0
                        fnew_f_last_mod = ''

                        exec_cmd = '{0} {1}'.format(mediainfo_tool, chkfile).split()
                        (org_h, org_w, org_last_mod, org_size) = run_command(exec_cmd)
                        org_file = root + '\\org_' + isrc + '.' + pic_tail
                        check_remove(org_file)
                        short_msg = str(org_w) + 'x' + str(org_h) + ':' + str(org_size) + ', '  + org_last_mod
                        if ((org_h == 0) or (org_w == 0)):
                            logfp.write(' FAIL, ' + short_msg + '\n')
                            failfp.write(chkfile + ', ' + short_msg + '\n')
                            continue

                        if ((int(org_h) > f_pic) or (int(org_w) > f_pic) or (int(org_size) > t_size)):
                            is_fail = 1
                            new_file = root + '\\new_' + isrc + '.' + pic_tail
                            os.system('\"{0}\" {1} -resize {2}x{2} -quality 50 {3}'.format(convert_tool, chkfile, f_pic, new_file))
                            exec_cmd = '{0} {1}'.format(mediainfo_tool, new_file).split()
                            (fnew_h, fnew_w, new_f_last_mod, fnew_size) = run_command(exec_cmd)
                            new2_file = root + '\\new2_' + isrc + '.' + pic_tail
                            os.system('{0} -loglevel 0 -i {1} -q:v 5 -vf scale=\"\'if(gt(a,1/1),{2},-1)\':\'if(gt(a,1/1),-1,{2})\'\" -y {3}'.format(ffmpeg_tool, chkfile, f_pic, new2_file))
                            exec_cmd = '{0} {1}'.format(mediainfo_tool, new2_file).split()
                            (ffnew_h, ffnew_w, fnew_f_last_mod, ffnew_size) = run_command(exec_cmd)
                            
                            if ((int(org_size) > int(fnew_size)) or (int(org_size) > int(ffnew_size))):
                                keep_file = new_file
                                #print(chkfile + str(org_size) + ',' + str(fnew_size) + ',' + str(ffnew_size) + '\n')
                                if (int(fnew_size) > int(ffnew_size)):
                                    keep_file = new2_file
                                    fnew_w = ffnew_w
                                    fnew_h = ffnew_h
                                    fnew_size = ffnew_size
                                    new_f_last_mod = fnew_f_last_mod

                                try:
                                    check_remove(chkfile)
                                    shutil.move(keep_file, chkfile)
                                    is_fail = 2
                                    i = i - 1
                                except:
                                    print("\n".format(chkfile))
                                    print("Unexpected error: {}\n".format(sys.exc_info()))
                                    print("Unexpected error: {}\n".format(traceback.format_list(traceback.extract_tb(sys.exc_info()[2]))))
                            else:
                                is_fail = 0
                            check_remove(new_file)
                            check_remove(new2_file)
                                    
                        if (is_fail ==0):
                            logfp.write(' OK, ' + short_msg + '\n')
                            okfp.write(chkfile + ', ' + short_msg + '\n')
                        elif (is_fail ==1):
                            logfp.write(' FAIL, ' + short_msg + '\n')
                            failfp.write(chkfile + ', ' + short_msg + '\n')
                        else:
                            long_msg = str(org_w) + 'x' + str(org_h) + ':' + str(org_size) + ', '  + str(fnew_w) + 'x' + str(fnew_h) + ':' + str(fnew_size) + ',' + org_last_mod +  ', ' + new_f_last_mod + '\n'
                            logfp.write(' TRANS, ' + long_msg)
                            tranfp.write(chkfile + ', ' + long_msg)
                    else:
                        logfp.write('\tskip ' + chkfile + '...\n')
                    if (i < 0):
                        break
                else:
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
    
