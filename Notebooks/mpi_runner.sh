NP=5
RES=15
RES_IN=15
START=600
RA_EXP=7
VISC_EXP=4.5
WIDTH=1
EXPT_DESC="tau_y_ii"


DRYRUN=0
STEPS=201

CMD="mpirun"
if (($DRYRUN))
then
    CMD="echo mpirun"
fi

# first run may be different (not restart, or its a change in resolution etc)

$CMD -np ${NP} python3 Convection_Cartesian.py \
        -uw_resolution ${RES} \
        -uw_resolution_in ${RES_IN} -uw_restart_step $START\
        -uw_ra_expt ${RA_EXP} -uw_visc_expt ${VISC_EXP} \
        -uw_width $WIDTH \
        -uw_expt_description ${EXPT_DESC} \
        -uw_max_steps $((STEPS+1))


for ((n = 1; n < 1; n++))
do
    let s0=START+STEPS*n
    echo running $STEPS more steps, starting at $s0
    $CMD -np ${NP} python3 Convection_Cartesian.py \
            -uw_resolution ${RES} \
            -uw_restart_step $s0 \
            -uw_ra_expt ${RA_EXP} -uw_visc_expt ${VISC_EXP} \
            -uw_width $WIDTH \
            -uw_expt_description ${EXPT_DESC} \
            -uw_max_steps $((STEPS+1))


done
