# # Rayleigh-Bénard Convection in an annulus
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

r_o = 1
r_i = 0.2

# Parameters that define the notebook
# These can be set when launching the script as
# mpirun python3 scriptname -uw_resolution=0.1 etc

ra_expt = uw.options.getReal("ra_expt",6) 
resolution = uw.options.getInt("resolution", default=15)
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
output_dir = os.path.join("output","annulus",f"Ra1e{ra_expt}")

os.makedirs(output_dir, exist_ok=True)


# +
## Set up the mesh geometry / discretisation


meshball = uw.meshing.Annulus(
    radiusInner=r_i, 
    radiusOuter=r_o, 
    cellSize=1/resolution, 
    degree=1, 
    qdegree=4, 
)

meshball.return_coords_to_bounds = None
meshball.dm.view()

uw.mpi.barrier()

x,y  = meshball.CoordinateSystem.X
r, th = meshball.CoordinateSystem.R
r_vector = meshball.CoordinateSystem.unit_e_0

# -

v_soln = uw.discretisation.MeshVariable("U", meshball, meshball.dim, degree=2)
p_soln = uw.discretisation.MeshVariable("P", meshball, 1, degree=1)
t_soln = uw.discretisation.MeshVariable("T", meshball, 1, degree=3)

# +
## Rigid body rotation mode - we want to remove this later

v_rigid_body = meshball.CoordinateSystem.unit_e_1 * meshball.CoordinateSystem.R[0]

I_rigid_body = uw.maths.Integral(meshball, v_rigid_body.dot(v_rigid_body))
vrb_norm = I_rigid_body.evaluate()

I_rigid_body.fn = v_soln.sym.dot(v_rigid_body)
vrb_mag = I_rigid_body.evaluate() / vrb_norm

vrb = lambda : I_rigid_body.evaluate() / vrb_norm

# +
# passive_swarm = uw.swarm.Swarm(mesh=meshball)
# passive_swarm.populate(fill_param=3)

# +
# Create solver to solver the momentum equation (Stokes flow)

stokes = Stokes(
    meshball, 
    velocityField=v_soln, 
    pressureField=p_soln, 
    solver_name="stokes",
)

stokes.constitutive_model = uw.constitutive_models.ViscousFlowModel
stokes.constitutive_model.Parameters.viscosity = 1.0

stokes.tolerance = 0.001

# Penalise flow crossing the boundary

r_boundary = r_vector

stokes.add_natural_bc(10*rayleigh_number * v_soln.sym.dot(r_boundary) * r_boundary, "Upper")
stokes.add_natural_bc(10*rayleigh_number * v_soln.sym.dot(r_boundary) * r_boundary, "Lower")

stokes.bodyforce = r_vector * rayleigh_number * t_soln.sym[0]

# +
# Create solver for the energy equation (Advection-Diffusion of temperature)

adv_diff = uw.systems.AdvDiffusion(
    meshball,
    u_Field=t_soln,
    V_fn=v_soln,
    solver_name="adv_diff",
    order=3,
)

adv_diff.constitutive_model = uw.constitutive_models.DiffusionModel
adv_diff.constitutive_model.Parameters.diffusivity = 1

## Boundary conditions for this solver

adv_diff.add_dirichlet_bc(1.0, "Lower")
adv_diff.add_dirichlet_bc(0.0, "Upper")

# +
# The advection / diffusion equation is an initial value problem
# We set this up to have 

abs_r = sympy.sqrt(meshball.rvec.dot(meshball.rvec))
init_t = 0.25 * sympy.sin(20.0 * th) * sympy.sin(np.pi * (r - r_i) / (r_o - r_i)) + (
    r_o - r
) / (r_o - r_i)


with meshball.access(t_soln):
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
# -

with meshball.access(v_soln):
    vrb_magnitude = vrb()
    v_soln.data[...] -= uw.function.evaluate(v_rigid_body * vrb_magnitude, v_soln.coords)

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
    stokes.solve(zero_init_guess=False)

    with meshball.access(v_soln):
        vrb_magnitude = vrb()
        v_soln.data[...] -= uw.function.evaluate(v_rigid_body * vrb_magnitude, v_soln.coords)
        
    delta_t = 2.0 * stokes.estimate_dt()
    adv_diff.solve(timestep=delta_t)

    # stats then loop
    tstats = t_soln.stats()

    if uw.mpi.rank == 0:
        print(f"Timestep {timestep}, dt {delta_t}, t {elapsed_time}")

    meshball.write_timestep(filename=f"{expt_name}",
                            index=timestep,
                            outputPath=output_dir,
                            meshVars=[v_soln, p_soln, t_soln],
                        )

    timestep += 1
    elapsed_time += delta_t


