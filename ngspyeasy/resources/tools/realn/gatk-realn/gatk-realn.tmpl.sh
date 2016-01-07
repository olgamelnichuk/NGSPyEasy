#!/usr/bin/env bash

time java -Xmx12g -Djava.io.tmpdir=${TMP_DIR} -jar /usr/local/bin/GenomeAnalysisTK.jar \
-T RealignerTargetCreator \
-nt ${NCPU} \
-R ${REFFASTA} \
-l INFO \
--unsafe ALL \
--validation_strictness SILENT \
-known ${KNOWN_INDELS} \
--mismatchFraction 0.30 \
--maxIntervalSize 650 \
-I ${DUPEMARK_BAM} \
-o ${DUPEMARK_BAM_FOR_INDER_REALN_INTERVALS} && \
time java -Xmx12g -Djava.io.tmpdir=${TMP_DIR} -jar /usr/local/bin/GenomeAnalysisTK.jar \
-T IndelRealigner \
-R ${REFFASTA} \
-l INFO \
--unsafe ALL \
--validation_strictness SILENT \
-I ${DUPEMARK_BAM} \
--maxReadsInMemory 300000 \
--maxReadsForRealignment 50000 \
--maxReadsForConsensuses 500 \
--maxConsensuses 100 \
--targetIntervals ${DUPEMARK_BAM_FOR_INDER_REALN_INTERVALS} \
-o ${DUPEMARK_REALN_BAM} && \
sambamba index ${DUPEMARK_REALN_BAM}
sambamba flagstat -t ${NCPU} ${DUPEMARK_REALN_BAM} > ${DUPEMARK_REALN_FLAGSTAT} && \
bedtools bamtobed -i ${DUPEMARK_REALN_BAM} | bedtools merge > ${DUPEMARK_REALN_BED} && \
rm -rf ${TMP_DIR}