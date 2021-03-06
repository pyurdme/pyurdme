""" pyurdme model for a single species diffusing on the unit square. """

import dolfin
import pyurdme
import numpy

class simple_diffusion(pyurdme.URDMEModel):
    """ Initial condition is a delta function at the center voxel. 
        The solution should be a Gaussian, up to the point where
        the BC becomes important. """

    def __init__(self):
    
        pyurdme.URDMEModel.__init__(self,name="simple_diffusion")

        D = 0.01
        A = pyurdme.Species(name="A",diffusion_constant=D,dimension=2)

        self.add_species([A])

        # A unit square
        self.mesh = pyurdme.URDMEMesh.generate_unit_square_mesh(40,40)
                
        # Place the A molecules in the voxel nearest the center of the square
        self.set_initial_condition_place_near({A:100000},point=[0.5,0.5])

        self.timespan(numpy.linspace(0,5,200))


if __name__ == '__main__':

    model = simple_diffusion()
    result = model.run()

    # Dump a snapshot of the state in paraview format. To visualize the solution,
    # open output/trajectory.pvd in ParaView.
    result.export_to_vtk("A", "output")
