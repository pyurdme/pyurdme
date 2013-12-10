""" pyURDME model file for the MinCDE example. """

import os

from pyurdme import pyurdme
#from pyurdme.pyurdme import *
import dolfin
import numpy

class Membrane(dolfin.SubDomain):
    def inside(self,x,on_boundary):
        return on_boundary


class Cytosol(dolfin.SubDomain):
    def inside(self,x,on_boundary):
        return not on_boundary


class mincde(pyurdme.URDMEModel):

    def __init__(self,model_name="mincde"):
        pyurdme.URDMEModel.__init__(self,model_name)

        # Species
        # TODO: We need a way to localize species to subdomains/boundaries
        MinD_m     = pyurdme.Species(name="MinD_m",diffusion_constant=1,dimension=2)
        MinD_c_atp = pyurdme.Species(name="MinD_c_atp",diffusion_constant=2.5e-12,dimension=3)
        MinD_c_adp = pyurdme.Species(name="MinD_c_adp",diffusion_constant=2.5e-12,dimension=3)
        MinD_e     = pyurdme.Species(name="MinD_e",diffusion_constant=2.5e-12,dimension=3)
        MinDE      = pyurdme.Species(name="MinDE",diffusion_constant=1e-14,dimension=2)
        
        self.addSpecies([MinD_m,MinD_c_atp,MinD_c_adp,MinD_e,MinDE])

        # Load mesh in dolfins xml format

        # This (below) hangs for unknown reason...
        # Build CSG Coli using Dolfin.
        #sphere1 = dolfin.Sphere(dolfin.Point(0,0,2.25),0.5)
        #sphere2 = dolfin.Sphere(dolfin.Point(0,0,-2.25),0.5)
        cylinder = dolfin.Cylinder(dolfin.Point(0,0,2.25),dolfin.Point(0,0,-2.25),0.5)
        #dolfin.plot(cylinder+sphere1+sphere2)
        #geom = cylinder+sphere1+sphere2
        self.mesh = pyurdme.Mesh(dolfin.Mesh(cylinder,30))
        #dolfin.info(self.mesh)
        #dolfin.plot(self.mesh)
        #dolfin.interactive()
        
        #self.mesh = pyurdme.read_dolfin_mesh("mesh/coli.xml")
        
        
        # Read the facet and interior cell physical domain markers into a Dolfin MeshFunction
        
        # TODO:  There is an issue here in that FeniCS dolfin-convert writes the value 0 for all the faces that
        # are not on the boundary. I think we migth have to write our own Gmsh2Dolfin converter.
        #file_in = dolfin.File("mesh/coli_facet_region.xml")
        #facet_function = dolfin.MeshFunction("size_t",self.mesh)
        #file_in >> facet_function
        
        #file_in = dolfin.File("mesh/coli_physical_region.xml")
        #physical_region = dolfin.MeshFunction("size_t",self.mesh)
        #file_in >> physical_region
        
        interior = dolfin.CellFunction("size_t",self.mesh)
        interior.set_all(1)
        #physical_region = dolfin.MeshFunction("size_t",self.mesh,self.mesh.topology().dim())
        #physical_region.set_all(1)


        boundary = dolfin.FacetFunction("size_t",self.mesh)
        #       facet_function = dolfin.MeshFunction("size_t",self.mesh,self.mesh.topology().dim()-1)
        boundary.set_all(0)
        #   facet_function.set_all(0)
        # Mark the boundary points
        membrane = Membrane()
        # interior = Cytosol()
        #membrane.mark(facet_function,74)
        #interior.mark(subdomains,5)
        #boundary = [2]
        membrane.mark(boundary,74)
        self.subdomains = [interior,boundary]
        #self.subdomains = [physical_region, facet_function]
        # Average mesh size to feed into the propensity functions
        hmax = self.mesh.hmax()
        hmin = self.mesh.hmin()
        h = (hmax+hmin)/2

        # Parameters
        NA = pyurdme.Parameter(name="NA",expression="6.022e23")
        #sigma_d  = Parameter(name="sigma_d",expression=2.5e-8/hmin)
        #sigma_dD = Parameter(name="sigma_dD",expression="9.0e6/(1000.0*NA)")
        #sigma_e  = Parameter(name="sigma_e",expression="5.56e7/(1000.0*NA)")
        #sigma_de = Parameter(name="sigma_de",expression=0.7)
        #sigma_dt = Parameter(name="sigma_dt",expression=1.0)
        
        sigma_d  = pyurdme.Parameter(name="sigma_d",expression=0.0)
        sigma_dD = pyurdme.Parameter(name="sigma_dD",expression=0.0)
        sigma_e  = pyurdme.Parameter(name="sigma_e",expression=0.0)
        sigma_de = pyurdme.Parameter(name="sigma_de",expression=0.0)
        sigma_dt = pyurdme.Parameter(name="sigma_dt",expression=0.0)
        
        self.addParameter([NA,sigma_d,sigma_dD,sigma_e,sigma_de,sigma_dt])

        # List of Physical domain markers that match those in the  Gmsh .geo file.
        boundary = [74]
        interior = [1]
        
        # Reactions
        R1 = pyurdme.Reaction(name="R1",reactants={MinD_c_atp:1},products={MinD_m:1},massaction=True,rate=sigma_d, restrict_to=boundary)
        R2 = pyurdme.Reaction(name="R2",reactants={MinD_c_atp:1,MinD_m:1},products={MinD_m:2},massaction=True,rate=sigma_dD,restrict_to=boundary)
        R3 = pyurdme.Reaction(name="R3",reactants={MinD_m:1,MinD_e:1},products={MinDE:1},massaction=True,rate=sigma_e,restrict_to=boundary)
        R4 = pyurdme.Reaction(name="R4",reactants={MinDE:1},products={MinD_c_adp:1,MinD_e:1},massaction=True,rate=sigma_de,restrict_to=boundary)
        R5 = pyurdme.Reaction(name="R5",reactants={MinD_c_adp:1},products={MinD_c_atp:1},massaction=True,rate=sigma_dt)
        R6 = pyurdme.Reaction(name="R6",reactants={MinDE:1,MinD_c_atp:1},products={MinD_m:1,MinDE:1},massaction=True,rate=sigma_dD,restrict_to=boundary)
        
        self.addReaction([R1,R2,R3,R4,R5,R6])
        
        # Restrict to boundary
        self.restrict(MinD_m,boundary)
        self.restrict(MinDE,boundary)
        
        # Distribute molecules randomly over the mesh according to their initial values
        self.scatter({MinD_m:1000},subdomains=boundary)
        #self.scatter({MinD_c_adp:4500})
        #self.scatter({MinD_e:1575},subdomains=boundary)


#self.timespan(numpy.linspace(0,1,100));
        self.timespan(range(100))

if __name__=="__main__":
    """ Dump model to a file. """
                     
    model = mincde(model_name="mincde")
    model.serialize("debug_input.mat")
    result = pyurdme.urdme(model)

    U = result["U"]
    print numpy.sum(U[::5,:],axis=0)
    pyurdme.dumps(model,"MinD_m","mindout")
    pyurdme.toXYZ(model,'mindm.xyz',file_format="VMD")
    
