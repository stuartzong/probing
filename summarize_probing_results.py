#! /usr/bin/env python

import os
import os.path
import datetime
import argparse
import csv
import logging
from pprint import pprint


def parse_probing_result(patient, probing_summary_file, results, gene_patients):
    # results = dict()
    # patient = 'L52'
    with open(probing_summary_file, 'r') as fh:
        for line in fh:
            sl = line.split('\t(')
            # print sl
            gene = sl[0].split(':')[0]
            probe = sl[0]
            hits = sl[1].split(' hits')[0]
            if int(hits) > 2:
                try:
                    results[gene][probe][patient].append(hits)
                except KeyError:
                    if gene not in results:
                        results[gene] = {}
                    if probe not in results[gene]:
                        results[gene][probe] = {}
                    results[gene][probe][patient] = [hits]

                try:
                    gene_patients[gene].append(patient)
                except KeyError:
                    gene_patients[gene] = [patient]
    for gene in gene_patients:
        gene_patients[gene] = list(set(gene_patients[gene]))
    # print(results)
    return (results, gene_patients)
            
def parse_files(probing_summary_paths):
    results = dict()
    gene_patients = dict()
    with open(probing_summary_paths, 'r') as fh:
        records = csv.DictReader(fh, delimiter='\t')
        for line in records:
            patient = line['patient']
            probing_summary_file = line['path']
            (results,
             gene_patients) = parse_probing_result(patient,
                                                   probing_summary_file,
                                                   results,
                                                   gene_patients)
    pprint(results)
    return (results, gene_patients)


def write_summary(results, gene_patients, final_summary):
    with open(final_summary, 'wb') as opf:
        writer = csv.writer(opf, delimiter='\t')
        headers = ['gene', 'num_genes',
                   'probe', 'num_probes',
                   'patient',
                   'num_patient_gene_level',
                   'num_patient_variant_level',
                   'probing_hits']
        writer.writerow(headers)
        num_genes = str(len(results))
        for gene in results:
            num_probes = str(len(results[gene]))
            num_patient_gene_level = str(len(gene_patients[gene]))
            for probe in results[gene]:
                num_patient_variant_level = str(len(results[gene][probe]))
                for patient in results[gene][probe]:
                    hits = str(results[gene][probe][patient][0])
                    # print "\t".join([gene, num_genes, probe, num_probes, patient, num_patient_ge0ne_level, num_patients])
                    writer.writerow([gene, num_genes,
                                     probe, num_probes,
                                     patient,
                                     num_patient_gene_level,
                                     num_patient_variant_level,
                                     hits])

def parse_args():
    parser = argparse.ArgumentParser(
        description='Filter variants based on qulaity and somatic filters')
    parser.add_argument(
        '-i', '--integration_summary_paths', required=True,
        help='specify input file, which contains all summary file paths.\
              column 1 header is patient, and column 2 header is path.')
    args = parser.parse_args()
    return args


def main():
    start = datetime.datetime.now()
    print("script starts at: %s" % start)
    args = parse_args()
    probing_summary_paths = args.integration_summary_paths
    # probing_summary_paths = '/projects/trans_scratch/validations/workspace/szong/luterlot/probing/transcriptome/L52/probing-2.2.3/HS0660/exon_boundary_snp_probes/HS0660.26.probes.summary'
    # parse_probing_result(probing_summary_paths)
    (results, gene_patients) = parse_files(probing_summary_paths)
    final_summary = 'probing_final_summary.txt'
    write_summary(results, gene_patients, final_summary)

    end = datetime.datetime.now()
    print("script ends at: %s" % end)


if __name__ == '__main__':
    main()
