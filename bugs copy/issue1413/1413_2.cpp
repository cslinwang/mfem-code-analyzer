#include "mfem.hpp"
#include <fstream>
#include <iostream>

using namespace std;
using namespace mfem;
int main(int argc, char *argv[])
{
    const char *mesh_file = "/root/mfem/mfem/data/beam-quad.mesh";

    Mesh *mesh = new Mesh(mesh_file, 1, 1);
    int dim = mesh->Dimension();
    int ref_levels = 5;
    for (int l = 0; l < ref_levels; l++) {
        mesh->UniformRefinement();
    }


    FiniteElementCollection *h1_fec = new H1_FECollection(1,dim);
    FiniteElementSpace *h1_fespace = new FiniteElementSpace(mesh, h1_fec);
    FiniteElementSpace *h1_fespace_flux = new FiniteElementSpace(mesh, h1_fec,dim);

    Vector flux_vec(2);
    flux_vec(0) = 1.0;
    flux_vec(1) = 1.0;
    VectorConstantCoefficient flux_coeff(flux_vec);

    GridFunction flux_func(h1_fespace_flux);
    flux_func.ProjectCoefficient(flux_coeff);

    VectorGridFunctionCoefficient flux_coef_vec(&flux_func);

    Array<int> flux_bdr;
    if (mesh->bdr_attributes.Size())
    {
        flux_bdr.SetSize(mesh->bdr_attributes.Max());
        flux_bdr = 0;
        if (mesh->bdr_attributes.Max()>1) flux_bdr[1] = 1;
    }

    LinearForm * flux_lf = new LinearForm(h1_fespace);
    flux_lf->AddBoundaryIntegrator(new BoundaryNormalLFIntegrator(flux_coef_vec), flux_bdr);
    flux_lf->Assemble();
    GridFunction one_gf(h1_fespace);
    ConstantCoefficient onecoeff(1.0);
    one_gf.ProjectCoefficient(onecoeff);

    double flux = flux_lf->operator()(one_gf);
    std::cout << "flux value: " << flux << std::endl;

    delete h1_fespace_flux;
    delete h1_fespace;
    delete h1_fec;
    delete mesh;
}
