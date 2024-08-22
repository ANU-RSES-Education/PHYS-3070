# # Rayleigh-Bénard Convection in an flat layer
#
#

# +
import mpi4py
import underworld3 as uw

from underworld3.systems import Stokes
from underworld3 import function

import numpy as np
import sympy
import os


# +
# The problem setup 

# mesh parameters

width = 6

# Parameters that define the notebook
# These can be set when launching the script as
# mpirun python3 scriptname -uw_resolution=0.1 etc

ra_expt = uw.options.getReal("ra_expt", default=4) 
resolution = uw.options.getInt("resolution", default=8)
max_steps = uw.options.getInt("max_steps", default=201)
restart_step = uw.options.getInt("restart_step", default=-1)
expt_desc = uw.options.getString("expt_description", default="")

if expt_desc != "":
    expt_desc += "_"

print(f"Restarting from step {restart_step}")

# How that works

rayleigh_number = uw.function.expression(r"\textrm{Ra}", 
                                         pow(10,ra_expt), # / (r_o-r_i)**3 , 
                                         "Rayleigh number")

expt_name = f"{expt_desc}Ra1e{ra_expt}_res{resolution}"
output_dir = os.path.join("output","cartesian",f"Ra1e{ra_expt}")

os.makedirs(output_dir, exist_ok=True)


# +
## Set up the mesh geometry / discretisation


meshbox = uw.meshing.UnstructuredSimplexBox(
    cellSize=1/resolution,
    minCoords=(0.0,0.0),
    maxCoords=(width,1.0), 
    degree=1, 
    qdegree=3,
)

# meshbox.return_coords_to_bounds = None
meshbox.dm.view()

x,y  = meshbox.CoordinateSystem.X
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

stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.viscosity = 1.0

stokes.tolerance = 0.00001

penalty = max(1000000, 10*rayleigh_number.sym)

# Prevent flow crossing the boundaries

# stokes.add_natural_bc(penalty * v_soln.sym[1] * y_vector, "Top")
# stokes.add_natural_bc(penalty * v_soln.sym[1] * y_vector, "Bottom")
# stokes.add_natural_bc(penalty * v_soln.sym[0] * x_vector, "Left")
# stokes.add_natural_bc(penalty * v_soln.sym[0] * x_vector, "Right")

stokes.add_essential_bc((None, 0.0), "Top")
stokes.add_essential_bc((None, 0.0), "Bottom")
stokes.add_essential_bc((0.0, None), "Left")
stokes.add_essential_bc((0.0, None), "Right")

stokes.bodyforce = y_vector * rayleigh_number * t_soln.sym[0]

# +
# Create solver for the energy equation (Advection-Diffusion of temperature)

adv_diff = uw.systems.AdvDiffusion(
    meshbox,
    u_Field=t_soln,
    V_fn=v_soln,
    solver_name="adv_diff",
    order=2,
)

adv_diff.constitutive_model = uw.constitutive_models.DiffusionModel
adv_diff.constitutive_model.Parameters.diffusivity = 1

## Boundary conditions for this solver

adv_diff.add_dirichlet_bc(1.0, "Bottom")
adv_diff.add_dirichlet_bc(0.0, "Top")


# +
# The advection / diffusion equation is an initial value problem
# We set this up to have 

init_t =  0.25 * sympy.cos(8.0 * sympy.pi * x) * sympy.sin(sympy.pi * y) + (1-y)

with meshbox.access(t_soln):
    t_soln.data[...] = uw.function.evaluate(init_t, t_soln.coords).reshape(-1, 1)

if restart_step != -1:
    print(f"Reading step {restart_step}")
    t_soln.read_timestep(data_filename=f"{expt_name}",
                         data_name="T",
                         index=restart_step,
                         outputPath=output_dir)


# +
# Solution strategy: solve for the velocity field, then update the temperature field.
# First we check this works for a tiny timestep, later we will repeat this to 
# model the passage of time.

stokes.solve()
adv_diff.solve(timestep=0.00001 * stokes.estimate_dt())

# +
if restart_step == -1:
    timestep = 0
else:
    timestep = restart_step
    
elapsed_time=0.0

# +
# Convection model / update in time

output = os.path.join(output_dir, expt_name)

for step in range(0, max_steps):
    
    stokes.solve(zero_init_guess=True)
    with meshbox.access(v_soln):
        v_soln.data[...] = 0.0
        
    delta_t = adv_diff.estimate_dt()
    adv_diff.solve(timestep=delta_t)

    # stats then loop
    tstats = t_soln.stats()

    if uw.mpi.rank == 0:
        print(f"Timestep {timestep}, dt {delta_t}, t {elapsed_time}")

    meshbox.write_timestep(filename=f"{expt_name}",
                            index=timestep,
                            outputPath=output_dir,
                            meshVars=[v_soln, p_soln, t_soln],
                        )

    timestep += 1
    elapsed_time += delta_t


