#include "mfem.hpp"
#include <fstream>
#include <iostream>

using namespace std;
using namespace mfem;

GridFunction* ProlongToMaxOrder(const GridFunction *x)
{
    const FiniteElementSpace *fespace = x->FESpace();
    const FiniteElementCollection *fec = fespace->FEColl();
    Mesh *mesh = fespace->GetMesh();

    int max_order = fespace->GetMaxElementOrder();
    std::cout << "max_order is " << max_order << std::endl;
    // Create a visualization space of max order for all elements
    FiniteElementCollection *vis_fec =
        new L2_FECollection(max_order, mesh->Dimension(), BasisType::GaussLobatto);
    FiniteElementSpace *vis_space =
        new FiniteElementSpace(mesh, vis_fec);

    IsoparametricTransformation T;
    DenseMatrix I;

    GridFunction *visualization_x = new GridFunction(vis_space);

    // Interpolate solution vector in the visualization space
    for (int i = 0; i < mesh->GetNE(); i++)
    {
        Geometry::Type geometry = mesh->GetElementGeometry(i);
        T.SetIdentityTransformation(geometry);

        Array<int> dofs;
        fespace->GetElementDofs(i, dofs);
        Vector elemvect, visualization_vect;
        x->GetSubVector(dofs, elemvect);

        const auto *fe = fec->GetFE(geometry, fespace->GetElementOrder(i));
        const auto *visualization_fe = vis_fec->GetFE(geometry, max_order);

        visualization_fe->GetTransferMatrix(*fe, T, I);
        vis_space->GetElementDofs(i, dofs);
        visualization_vect.SetSize(dofs.Size());

        I.Mult(elemvect, visualization_vect);
        visualization_x->SetSubVector(dofs, visualization_vect);
    }

    visualization_x->MakeOwner(vis_fec);
    return visualization_x;
}

int main(int argc, char *argv[])
{
    int order = 2;
    bool visualization = true;

    OptionsParser args(argc, argv);
    args.AddOption(&order, "-o", "--order",
                   "Finite element order (polynomial degree) or -1 for"
                   " isoparametric space.");
    args.AddOption(&visualization, "-vis", "--visualization", "-no-vis",
                   "--no-visualization",
                   "Enable or disable GLVis visualization.");
    args.Parse();
    if (!args.Good())
    {
        args.PrintUsage(cout);
        return 1;
    }
    args.PrintOptions(cout);

    Mesh mesh = Mesh::MakeCartesian2D(2, 1, Element::QUADRILATERAL);
    mesh.EnsureNCMesh(true);
    int dim = mesh.Dimension();

    {
        // h-refine element 1
        Array<Refinement> refinements;
        refinements.Append(Refinement(1));

        int nonconformity_limit = 0; // 0 meaning allow unlimited ratio
        mesh.GeneralRefinement(refinements, 1, nonconformity_limit);  // h-refinement
    }

    H1_FECollection fec(order, dim, BasisType::Positive);

    FiniteElementSpace fespace(&mesh, &fec);
    //fespace.SetRelaxedHpConformity(true);

    GridFunction x(&fespace);

    fespace.SetElementOrder(0, 3);

    fespace.Update(false);
    x.SetSpace(&fespace);

    ConstantCoefficient one;
    x.ProjectCoefficient(one);

    Table const& t = fespace.GetElementToDofTable();
    std::set<int> dofs;
    for (int i=0; i<t.Size(); ++i)
    {
        const int* r = t.GetRow(i);
        for (int j=0; j<t.RowSize(i); ++j)
            dofs.insert(r[j]);
    }

    for (int i=0; i<fespace.GetTrueVSize(); ++i)
    {
        auto it = dofs.find(i);
        if (it == dofs.end())
            cout << "DOF missing: " << i << endl;
    }

    // Enforce space constraints on locally interpolated GridFunction x
    const SparseMatrix *R = fespace.GetHpRestrictionMatrix();
    const SparseMatrix *P = fespace.GetConformingProlongation();

    if (P)
    {
        R->Print();
        Vector y(fespace.GetTrueVSize());
        fespace.GetHpRestrictionMatrix()->Mult(x, y);
        fespace.GetProlongationMatrix()->Mult(y, x);
    }

    GridFunction *px = ProlongToMaxOrder(&x);
    ofstream mesh_ofs("hp.mesh");
    mesh_ofs.precision(8);
    mesh.Print(mesh_ofs);
    ofstream sol_ofs("hp.gf");
    sol_ofs.precision(8);
    px->Save(sol_ofs);

    if (visualization)
    {
        char vishost[] = "localhost";
        int  visport   = 19916;
        socketstream sol_sock(vishost, visport);
        sol_sock.precision(8);
        sol_sock << "solution\n" << mesh << *px << flush;
    }

    return 0;
}