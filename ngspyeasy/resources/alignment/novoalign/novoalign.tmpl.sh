#!/usr/bin/env bash

time /usr/local/bin/novoalign \
-d ${GENOMEINDEX}.fasta.novoindex \
-f ${FQ1} ${FQ2} \
-F STDFQ \
--3Prime \
-g 40 \
-x 6 \
-i PE 500,100 \
-c ${NCPU} \
-k \
-K ${K_STATS} \
-o SAM $'@RG\tID:${BAM_PREFIX}\tSM:${BAM_PREFIX}\tPU:${NGS_PLATFORM}\tLB:${DNA_PREP_LIBRARY_ID}' | \
samblaster --addMateTags --excludeDups \
--discordantFile ${DISCORDANT_SAM} \
--splitterFile ${SPLITREAD_SAM} \
--unmappedFile ${UNMAPPED_FASTQ} | \
sambamba view -t ${NCPU} -S -f bam /dev/stdin | \
sambamba sort -t ${NCPU} -m 2GB --tmpdir=${TMP_DIR} -o ${DUPEMARK_BAM} /dev/stdin && \
sambamba index ${DUPEMARK_BAM} && \
sambamba flagstat -t ${NCPU} ${DUPEMARK_BAM} > ${DUPEMARK_FLAGSTAT_REPORT} && \
bedtools bamtobed -i ${DUPEMARK_BAM} | bedtools merge > ${DUPEMARK_BED_REPORT} && \
sambamba view -t ${NCPU} -S -f bam ${DISCORDANT_SAM} | \
sambamba sort -t ${NCPU} -m 2GB --tmpdir=${TMP_DIR} -o ${DISCORDANT_BAM} /dev/stdin && \
sambamba index ${DISCORDANT_BAM} && \
sambamba view -t ${NCPU} -S -f bam ${SPLITREAD_SAM} | \
sambamba sort -t ${NCPU} -m 2GB --tmpdir=${TMP_DIR} -o ${SPLITREAD_BAM} /dev/stdin && \
sambamba index ${SPLITREAD_BAM} && \
rm -v ${DISCORDANT_SAM} && \
rm -v ${SPLITREAD_SAM} && \
rm -rf ${TMP_DIR}/* && \
chmod -R 777 ${ALIGNMENTS_DIR}/*