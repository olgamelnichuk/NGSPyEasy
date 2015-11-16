#!/usr/bin/env bash

time /usr/local/pipeline/freebayes/scripts/freebayes-parallel <(/usr/local/pipeline/freebayes/scripts/fasta_generate_regions.py ${REFFASTA} 100000) ${NCPU} \
-f ${REFFASTA} \
-b ${VC_FILTERED_BAM} \
--min-coverage 2 \
--min-mapping-quality 10 \
--min-base-quality 10 \
--min-repeat-entropy 1 \
--genotype-qualities > ${FREEBAYES_RAW_VCF} && \
time cat ${FREEBAYES_RAW_VCF} | \
vcffilter -f 'QUAL > 5' -s | \
fix_ambiguous | \
vcfallelicprimitives --keep-geno | \
vcffixup - | \
vcfstreamsort | \
vt normalize -r ${REFFASTA} -q - 2> /dev/null | \
vcfuniqalleles | \
bgzip -c > ${FREEBAYES_VCF_GZ} && \
tabix ${FREEBAYES_VCF_GZ} && \
bgzip ${FREEBAYES_RAW_VCF} && \
tabix ${FREEBAYES_RAW_VCF_GZ}