NP=5
RES=25
RES_IN=25
START=698
RA_EXP=8
VISC_EXP=4
WIDTH=1
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
        -uw_max_steps $((STEPS+1))


for ((n = 1; n < 10; n++))
do
    let s0=START+STEPS*n
    echo running $STEPS more steps, starting at $s0
    $CMD -np ${NP} python3 Convection_Cartesian.py \
            -uw_resolution ${RES} \
            -uw_restart_step $s0 \
            -uw_ra_expt ${RA_EXP} -uw_visc_expt ${VISC_EXP} \
            -uw_width $WIDTH \
            -uw_max_steps $((STEPS+1))


done

# mpirun -np ${NP} python3 Convection_Cartesian.py -uw_resolution ${RES}
