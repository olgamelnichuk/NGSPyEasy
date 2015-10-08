#!/usr/bin/env bash

time java -Xmx12g -Djava.io.tmpdir=${SOUTDocker}/tmp -jar /usr/local/pipeline/picardtools/${PICARD_VERSION}/picard.jar CleanSam \
TMP_DIR=${TMP_DIR} \
CREATE_INDEX=FALSE \
VALIDATION_STRINGENCY=SILENT \
INPUT=${DUPEMARK_TMP_BAM} \
OUTPUT=${DUPEMARK_TMPCLEANSAM_BAM} && \
sambamba index ${DUPEMARK_TMPCLEANSAM_BAM}