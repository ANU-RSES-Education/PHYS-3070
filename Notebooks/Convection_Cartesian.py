# # Rayleigh-Bénard Convection in an flat layer
#
#

# +
import underworld3 as uw

import os
import numpy as np
import sympy

from underworld3.systems import Stokes
from underworld3 import function
import mpi4py

# -


# +
# The problem setup

# mesh parameters

width = 1

visc_exp = 4


# Parameters that define the notebook
# These can be set when launching the script as
# mpirun python3 scriptname -uw_resolution=0.1 etc

ra_expt = uw.options.getReal("ra_expt", default=6)
visc_expt = uw.options.getReal("visc_expt", default=0)
width = uw.options.getInt("width", default=1)
resolution = uw.options.getInt("resolution", default=15)
resolution_in = uw.options.getInt("resolution_in", default=-1)
max_steps = uw.options.getInt("max_steps", default=201)
restart_step = uw.options.getInt("restart_step", default=-1)
expt_desc = uw.options.getString("expt_description", default="")

if expt_desc != "":
    expt_desc += "_"

if uw.mpi.rank == 0:
    print(f"Restarting from step {restart_step}")

if resolution_in == -1:
    resolution_in = resolution

# How that works

rayleigh_number = uw.function.expression(
    r"\textrm{Ra}", pow(10, ra_expt), "Rayleigh number"  # / (r_o-r_i)**3 ,
)

old_expt_name = f"{expt_desc}Ra1e{ra_expt}_visc{visc_exp}_res{resolution_in}"
expt_name = f"{expt_desc}Ra1e{ra_expt}_visc{visc_exp}_res{resolution}"
output_dir = os.path.join("output", f"cartesian_{width}x1", f"Ra1e{ra_expt}")

os.makedirs(output_dir, exist_ok=True)


# +
## Set up the mesh geometry / discretisation

meshbox = uw.meshing.UnstructuredSimplexBox(
    cellSize=1 / resolution,
    minCoords=(0.0, 0.0),
    maxCoords=(width, 1.0),
    degree=1,
    qdegree=3,
    regular=False,
)

x, y = meshbox.CoordinateSystem.X
x_vector = meshbox.CoordinateSystem.unit_e_0
y_vector = meshbox.CoordinateSystem.unit_e_1

# -

v_soln = uw.discretisation.MeshVariable("U", meshbox, meshbox.dim, degree=2)
p_soln = uw.discretisation.MeshVariable("P", meshbox, 1, degree=1)
t_soln = uw.discretisation.MeshVariable("T", meshbox, 1, degree=3)

# +
# passive_swarm = uw.swarm.Swarm(mesh=meshbox)
# passive_swarm.populate(fill_param=3)

# +
# Create solver to solver the momentum equation (Stokes flow)

stokes = Stokes(
    meshbox,
    velocityField=v_soln,
    pressureField=p_soln,
    solver_name="stokes",
)

C = uw.function.expression("C", sympy.log(sympy.Pow(10, sympy.sympify(visc_exp))))
visc_fn = uw.function.expression(
    r"\eta",
    sympy.exp(-C.sym * t_soln.sym[0]) * sympy.Pow(10, sympy.sympify(visc_exp)),
    "1",
)

stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.shear_viscosity_0 = visc_fn

stokes.tolerance = 1e-6
stokes.penalty = 0.0

# penalty = max(1000000, 10*rayleigh_number.sym)

# Prevent flow crossing the boundaries

stokes.add_essential_bc((None, 0.0), "Top")
stokes.add_essential_bc((None, 0.0), "Bottom")
stokes.add_essential_bc((0.0, None), "Left")
stokes.add_essential_bc((0.0, None), "Right")

stokes.bodyforce = y_vector * rayleigh_number * t_soln.sym[0]
# -

stokes.constitutive_model.Parameters.shear_viscosity_0


visc_fn._expr_count

# +
# Create solver for the energy equation (Advection-Diffusion of temperature)

adv_diff = uw.systems.AdvDiffusion(
    meshbox,
    u_Field=t_soln,
    V_fn=v_soln,
    solver_name="adv_diff",
    order=1,
    verbose=False,
)

adv_diff.constitutive_model = uw.constitutive_models.DiffusionModel
adv_diff.constitutive_model.Parameters.diffusivity = 1

## Boundary conditions for this solver

adv_diff.add_dirichlet_bc(+1.0, "Bottom")
adv_diff.add_dirichlet_bc(-0.0, "Top")

# +
# The advection / diffusion equation is an initial value problem
# We set this up with an approximation to the ultimate boundary
# layer structure (you need to provide delta, the TBL thickness)
#
# Add some perturbation and try to offset this on the different boundary
# layers to avoid too much symmetry

delta = 0.2
aveT = 0.5 - 0.5 * (sympy.tanh(2 * y / delta) - sympy.tanh(2 * (1 - y) / delta))

init_t = (
    0.0 * sympy.cos(0.5 * sympy.pi * x) * sympy.sin(2 * sympy.pi * y)
    + 0.02 * sympy.cos(10.0 * sympy.pi * x) * sympy.sin(2 * sympy.pi * y)
    + aveT
)

with meshbox.access(t_soln):
    t_soln.data[...] = uw.function.evaluate(init_t, t_soln.coords).reshape(-1, 1)

if restart_step != -1:
    print(f"Reading step {restart_step} at resolution {resolution_in}")
    t_soln.read_timestep(
        data_filename=f"{old_expt_name}",
        data_name="T",
        index=restart_step,
        outputPath=output_dir,
    )


# +
# Solution strategy: solve for the velocity field, then update the temperature field.
# First we check this works for a tiny timestep, later we will repeat this to
# model the passage of time.

stokes.solve()
# adv_diff.solve(timestep=0.00001 * stokes.estimate_dt())

# +
if restart_step == -1:
    timestep = 0
else:
    timestep = restart_step

elapsed_time = 0.0

# +
# Convection model / update in time

output = os.path.join(output_dir, expt_name)

for step in range(0, max_steps):

    stokes.solve(zero_init_guess=False)

    delta_t = 2.0 * adv_diff.estimate_dt()
    delta_ta = stokes.estimate_dt()

    adv_diff.solve(timestep=delta_t)

    # stats then loop
    tstats = t_soln.stats()

    if uw.mpi.rank == 0:
        print(
            f"Timestep {timestep}, dt {delta_t:.4e}, dta {delta_ta:.4e}, t {elapsed_time:.4e} "
        )

    meshbox.write_timestep(
        filename=f"{expt_name}",
        index=timestep,
        outputPath=output_dir,
        meshVars=[v_soln, p_soln, t_soln],
    )

    timestep += 1
    elapsed_time += delta_t
