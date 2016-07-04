#!/usr/bin/env python

import os, stat, os.path, time, datetime, subprocess
import re, sys, glob, argparse, csv
from collections import defaultdict
from pprint import pprint
from itertools import islice
import fileinput
import shutil

# get key -> info dictionary from 2 files
def get_bams(infile):
    # infile contains patient, library, and bam file info
    with open(infile) as fh:
        libbam_dict = dict()
        records = csv.DictReader(fh,  delimiter='\t')
        headers = records.fieldnames
        for line in records:
            patient = line['patient']
            bam = line['bam']
            library = line['library']
            libbam_dict[library] = [patient, bam]
    pprint(libbam_dict)
    return (libbam_dict)

def add_bam_to_input_file(infile, libbam_dict):
    # infile contains all probing input file full path
    with open(infile) as fh:
        for probing_input_file in fh:
            probing_input_file = probing_input_file.strip()
            modified_file = '.'.join([probing_input_file, 'modified'])
            with open(modified_file, 'wb') as writer:
                print(probing_input_file)
                print(modified_file)
                library = probing_input_file.split('/')[10].split('_')[0]
                bam = libbam_dict[library][1]
                with open(probing_input_file) as fh2:
                    for line in fh2:
                        if (len(line.split(' ')) == 4):
                            content = ' '.join([bam] + [line])
                            writer.write(content)
                        else:
                            print('Input file has incorrect columns')
                            sys.exit()
                os.rename(modified_file, probing_input_file)


def make_probing_setup_commands(libbam_dict, probing_setup_commands):
    with open(probing_setup_commands, 'wb') as writer:
        for library in libbam_dict:
            patient = libbam_dict[library][0]
            writer.write(' '.join(['probing_setup',
                                   patient,
                                   # 'none',
                                   library,
                                   'none',
                                   'none 2.2.3']))
            writer.write('\n')

            
def qsub_scripts(script_files):
    with open(script_files, 'r') as fh:
        for line in fh:
            sl = line.rstrip().split('\t')
            wkdir = sl[0]
            script = sl[1]
            # print('ssh m0001 \"cd %s; bash %s\"' % (wkdir, script))
            p = subprocess.Popen('ssh tachpc \"cd %s;  bash %s\"' %
                                 (wkdir, script),  shell=True, stdout=subprocess.PIPE)
            output,  err = p.communicate()


def parse_args():
    parser = argparse.ArgumentParser(
        description='this script generate scripts to run probing pipeline.')
    parser.add_argument(
        '-i', '--bam_paths', required=True,
        help='specify input file containing info: patient, library, and bam path')
    args = parser.parse_args()
    return args

def get_probing_input_files(libbam_dict, outfile):
    with open(outfile, 'wb') as writer:
        wkdir = os.getcwd()
        for library in libbam_dict:
            patient = libbam_dict[library][0]
            content = ''.join([wkdir, '/',
                               patient,
                               '/probing-2.2.3/',
                               library,
                               # '_input_transcriptome.txt'])
                               '_input_tumour_genome.txt'])
            writer.write(content)
            writer.write('\n')

            
def get_qsub_scripts(libbam_dict, outfile):
    with open(outfile, 'wb') as writer:
        wkdir = os.getcwd()
        for library in libbam_dict:
            patient = libbam_dict[library][0]
            content = ''.join([wkdir, '/',
                               patient,
                               '/probing-2.2.3',
                               '\trun_probing.',
                               library,
                               '.sh'])
            writer.write(content)
            writer.write('\n')

def __main__():
    print "Scripts starts at: %s!" % datetime.datetime.now()     
    args = parse_args()
    bam_paths = args.bam_paths
    libbam_dict = get_bams(bam_paths)
    probing_setup_commands = 'probing_setup_commands.sh'
    # make_probing_setup_commands(libbam_dict, probing_setup_commands)
    # p = subprocess.Popen('bash %s' % probing_setup_commands,
    #                      shell=True, stdout=subprocess.PIPE)
    # output,  err = p.communicate()
    # # add bam path to probing input file
    # probing_input_files = 'probing_input_files.txt'
    # get_probing_input_files(libbam_dict, probing_input_files)
    # add_bam_to_input_file(probing_input_files, libbam_dict)
    # get all qsub_scripts path
    qsub_script_files = 'qsub_scripts.txt'
    # get_qsub_scripts(libbam_dict, qsub_script_files)
    
    qsub_scripts(qsub_script_files)

if __name__ == '__main__':
    __main__()
