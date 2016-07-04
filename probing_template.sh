#! /bin/bash

# This script run probing pipeline
# data_type = {{data_type}}

# setup probing directories, generate probing raw input files
probing_setup {{patient}}
              {{tumor_genome}}
              {{tumour_transcriptome}}
              {{normal_genome}}
              {{probing_version}}

