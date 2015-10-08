#!/usr/bin/env bash

time python  /usr/local/pipeline/${STAMPY_VERSION}/stampy.py \
-g ${GENOMEINDEX} \
-h ${GENOMEINDEX} \
-t ${NCPU} \
--bamsortprefix ${TMP_DIR} \
--bamkeepgoodreads \
--sanger \
--bwamark \
--baq \
--gapopen=40 \
--gapextend=6 \
--noautosense \
--insertsize=500 \
--insertsd=100 \
-M ${TMP_BAM} | \
samblaster --addMateTags --excludeDups \
--discordantFile ${DISCORDANT_SAM} \
--splitterFile ${SPLITREAD_SAM} \
--unmappedFile ${UNMAPPED_FASTQ} | \
sambamba view -t ${NCPU} -S -f bam /dev/stdin | \
sambamba sort -t ${NCPU} -m 2GB --tmpdir=${TMP_DIR} -o ${DUPEMARK_TMP_BAM} /dev/stdin && \
sambamba index ${DUPEMARK_TMP_BAM} && \
sambamba view -t ${NCPU} -S -f bam ${DISCORDANT_SAM} | \
sambamba sort -t ${NCPU} -m 2GB --tmpdir=${TMP_DIR} -o ${DISCORDANT_BAM} /dev/stdin && \
sambamba index ${DISCORDANT_BAM} && \
sambamba view -t ${NCPU} -S -f bam ${SPLITREAD_SAM} | \
sambamba sort -t ${NCPU} -m 2GB --tmpdir=${TMP_DIR} -o ${SPLITREAD_BAM} /dev/stdin && \
sambamba index ${SPLITREAD_BAM} && \
rm -v ${DISCORDANT_SAM} && \
rm -v ${SPLITER_SAM} && \
rm -rf ${TMP_DIR}/* && \
chmod -R 777 ${ALIGNMENTS_DIR}/*