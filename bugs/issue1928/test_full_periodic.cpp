//
// Compile with: make test_full_periodic
//
// Author: Guillaume Latu
//
// Description:  This example code solves a simple linear elasticity problem
//               describing a multi-material square.
//               This problem has a 1D analytic solution along x1 dimension,
//               the solution is constant along x2 dimension which is also periodic.
//
//               The geometry of the domain is assumed to be as
//               follows:
//
//                           x2=1  +----------+----------+
//                                 | material | material |
//                                 |    1     |    2     |
//                           x2=0  +----------+----------+
//                               x1=0                   x1=1
//
//
//               Specifically, we approximate the weak form of -div(sigma(u))=0
//               where sigma(u)=lambda*div(u)*I+mu*(grad*u+u*grad) is the stress
//               tensor corresponding to displacement field u, and lambda and mu
//               are the material Lame constants. The boundary conditions are
//               periodic.
//
//               Mechanical strain:
//                               eps = E + grad_s v
//
//                         with  E the given macrocoscopic strain
//                               v the periodic displacement fluctuation
//               Displacement:
//                                 u = U + v
//
//                         with  U the given displacement associated to E
//                                 E = grad_s U
//
//               The local microscopic strain is equal, on average, to the macroscopic strain:
//                         <eps> = <E>
//
//               Equation to be solved:   div(C grad_s v)= - div(C grad_s U)
//
//               Thus, we introduce the force term -div(C grad_s U) in addition to the
//               classical elasticity problem.
//

#include "mfem.hpp"
#include <fstream>
#include <iostream>

using namespace std;
using namespace mfem;

// central frontier in-between the two materials
const double xthr = 0.5;

/// Class for domain integrator L(v) := (f, grad v)
class DomainLFGrad2Integrator : public LinearFormIntegrator
{
protected:
  Coefficient *lambda, *mu;
private:
  Vector shape, Qvec, Svec;
  DenseMatrix dshape;
  int tcase;

public:
   /// Constructs the domain integrator (Q, grad v)
  DomainLFGrad2Integrator(Coefficient &l, Coefficient &m, int _tcase)
  {
    lambda = &l; mu = &m; tcase = _tcase;
  }

  void AssembleRHSElementVect(
    const FiniteElement &el, ElementTransformation &Tr, Vector &elvect)
  {
    int dof = el.GetDof();
    int spaceDim = Tr.GetSpaceDim();

    dshape.SetSize(dof, spaceDim);
    Qvec.SetSize(3);
    Svec.SetSize(3);
    elvect.SetSize(dof*spaceDim);
    elvect = 0.0;

    const IntegrationRule *ir = IntRule;
    if (ir == NULL)
      {
	int intorder = 2 * el.GetOrder();
	ir = &IntRules.Get(el.GetGeomType(), intorder);
      }

    for (int i = 0; i < ir->GetNPoints(); i++)
      {
	const IntegrationPoint &ip = ir->IntPoint(i);
	Tr.SetIntPoint(&ip);
	el.CalcPhysDShape(Tr, dshape);

	double M = mu->Eval(Tr, ip);
	double L = lambda->Eval(Tr, ip);
	switch(tcase) {
	case 1:
	  Svec[0]=0;Qvec[0] = -(L+2*M);
	  Svec[1]=1;Qvec[1] = -L;
	  Svec[2]=2;Qvec[2] = -L;
	  break;
	case 2:
	  Svec[0]=0;Qvec[0] = -L;
	  Svec[1]=1;Qvec[1] = -(L+2*M);
	  Svec[2]=2;Qvec[2] = -L;
	  break;
	case 3:
	  Svec[0]=0;Qvec[0] = -L;
	  Svec[1]=1;Qvec[1] = -L;
	  Svec[2]=2;Qvec[2] = -(L+2*M);
	  break;
	case 4:
	  Svec[0]=1;Qvec[0] = -M;
	  Svec[1]=0;Qvec[1] = -M;
	  Svec[2]=2;Qvec[2] = 0;
	  break;
	case 5:
	  Svec[0]=0;Qvec[0] = 0;
	  Svec[1]=2;Qvec[1] = -M;
	  Svec[2]=1;Qvec[2] = -M;
	  break;
	case 6:
	  Svec[0]=2;Qvec[0] = -M;
	  Svec[1]=1;Qvec[1] = 0;
	  Svec[2]=0;Qvec[2] = -M;
	  break;
	}
	Qvec *= ip.weight * Tr.Weight();
	for (int k = 0; k < spaceDim; k++)
	  {
	    for (int s = 0; s < dof; s++)
	      {
		elvect(dof*k+s)	+= Qvec[k]*dshape(s,Svec[k]);
	      }
	  }
      }
  }


};

void sol_exact1(const Vector &x, Vector &u);
void sol_exact2(const Vector &x, Vector &u);
void sol_exact3(const Vector &x, Vector &u);
void sol_exact4(const Vector &x, Vector &u);
void sol_exact5(const Vector &x, Vector &u);
void sol_exact6(const Vector &x, Vector &u);

int main(int argc, char *argv[])
{
   //    Parse command-line options.
   const char *mesh_file = "/root/mfem-code-analyzer/bugs/issue1928/square_2mat_per.msh";
   //   const char *mesh_file = "yper.mesh";
   int order = 1;
   int tcase = 1;
   bool static_cond = false;
   bool visualization = 1;

   OptionsParser args(argc, argv);
   args.AddOption(&mesh_file, "-m", "--mesh",
                  "Mesh file to use.");
   args.AddOption(&order, "-o", "--order",
                  "Finite element order (polynomial degree).");
   args.AddOption(&tcase, "-t", "--tcase",
                  "identifier of the case : Exx->1, Eyy->2, Ezz->3, Exy->4, Eyz->5, Exz->6");
   args.Parse();
   if (!args.Good())
   {
      args.PrintUsage(cout);
      return 1;
   }
   args.PrintOptions(cout);

   //   Read the mesh from the given mesh file. We can handle triangular,
   //    quadrilateral, tetrahedral or hexahedral elements with the same code.
   Mesh *mesh = new Mesh(mesh_file, 1, 1);
   int dim = mesh->Dimension();

   if ( dim == 2 && tcase != 1 && tcase != 2 && tcase != 4 ) {
     cout << "This test case is undefined in 2D" << endl;
     exit(1);
   }
   if ( dim == 3 && ((tcase < 1) || (tcase > 6))) {
     cout << "This test case is undefined in 3D" << endl;
     exit(1);
   }


   //    Define a finite element space on the mesh. Here we use vector finite
   //    elements, i.e. dim copies of a scalar finite element space. The vector
   //    dimension is specified by the last argument of the FiniteElementSpace
   //    constructor.
   FiniteElementCollection *fec;
   FiniteElementSpace *fespace;
   fec = new H1_FECollection(order, dim);
   fespace = new FiniteElementSpace(mesh, fec, dim);

   int ndof = fespace->GetTrueVSize() / dim;
   cout << "Number of finite element unknowns: " << fespace->GetTrueVSize() << " ndof: " << ndof << " dim: " << dim
        << endl << "Assembling: " << flush;

   //    Define the solution vector x as a finite element grid function
   //    corresponding to fespace. Initialize x with initial guess of zero,
   //    which satisfies the boundary conditions.
   GridFunction x(fespace);
   x = 0.;

   // Set up the bilinear form a(.,.) on the finite element space
   //    corresponding to the linear elasticity integrator with piece-wise
   //    constants coefficient lambda and mu.
   Vector lambda(mesh->attributes.Max());
   lambda = 100.0;
   if (mesh->attributes.Max() > 1)
     lambda(1) = lambda(0)*2;
   PWConstCoefficient lambda_func(lambda);
   Vector mu(mesh->attributes.Max());
   mu = 75.0;
   if (mesh->attributes.Max() > 1)
     mu(1) = mu(0)*2;
   PWConstCoefficient mu_func(mu);


   // Impose no displacement on the first node
   // which needs to be on x=xmin or x=xmax axis.
   // ux=0, uy=0, uz=0 on this point.
   Array<int> ess_tdof_list;
   ess_tdof_list.SetSize(dim);
   for (int k = 0; k < dim; k++)
     {
       int tgdof = 0+k*ndof;
       ess_tdof_list[k] = tgdof;
       x(tgdof) = 0.0;
     }

   BilinearForm *a = new BilinearForm(fespace);
   a->AddDomainIntegrator(new ElasticityIntegrator(lambda_func,mu_func));
   a->Assemble();

   // Set up the right-hand side of the FEM linear system.
   LinearForm rhs(fespace);
   rhs.AddDomainIntegrator(new DomainLFGrad2Integrator(lambda_func,mu_func,tcase));
   rhs.Assemble();

   // Assemble the bilinear form and the corresponding linear system,
   // applying any necessary transformations such as: eliminating boundary
   // conditions, applying conforming constraints for non-conforming AMR,
   // static condensation, etc.
   SparseMatrix A;
   Vector B, X;
   a->FormLinearSystem(ess_tdof_list, x, rhs, A, X, B);
   cout << "Size of linear system: " << A.Height() << endl;
   // Define a simple symmetric Gauss-Seidel preconditioner and use it to
   // solve the system Ax=b with PCG.
   GSSmoother M(A);
   PCG(A, M, B, X, 1, 500, 1e-20, 0.0);

   //  Recover the solution as a finite element grid function.
   a->RecoverFEMSolution(X, rhs, x);

   //  Save the result, the displacement u
   {
     ParaViewDataCollection paraview_dc("per", mesh);
     paraview_dc.RegisterField("u",&x);
     paraview_dc.SetCycle(0);
     paraview_dc.SetTime(0.0);
     paraview_dc.Save();
   }

   void (*sol_exact)(const Vector &x, Vector &u);
   switch(tcase) {
   case 1:
     sol_exact=sol_exact1;
     break;
   case 2:
     sol_exact=sol_exact2;
     break;
   case 3:
     sol_exact=sol_exact3;
     break;
   case 4:
     sol_exact=sol_exact4;
     break;
   case 5:
     sol_exact=sol_exact5;
     break;
   case 6:
     sol_exact=sol_exact6;
     break;
   default:
     cout << "Test undefined" << endl;
     exit (1);
     break;
   }
   VectorFunctionCoefficient sol_coef (dim, sol_exact);
   double errorL2 = x.ComputeL2Error(sol_coef);
   cout<<"\ntcase " << tcase << " -- L2 norm: " << errorL2 << endl;
   if (errorL2 < 1e-10)
     {
       cout << "OK" << endl;
       exit(0);
     }
   else
     {
       cout << "Fail" << endl;
       exit(1);
     }

   return 0;
}



void sol_exact1(const Vector &x, Vector &u)
{
  const double gradx = 1./3.;
  u =  0.;
  if (x(0) < xthr)
    {
      u(0) = gradx*x(0);
    }
  else
    {
      u(0) = gradx*xthr - gradx*(x(0)-xthr);
    }
}

void sol_exact2(const Vector &x, Vector &u)
{
  const double gradx = 4./30.;
  u =  0.;
  if (x(0) < xthr)
    {
      u(0) = gradx*x(0);
    }
  else
    {
      u(0) = gradx*xthr - gradx*(x(0)-xthr);
    }
}

void sol_exact3(const Vector &x, Vector &u)
{
  const double gradx = 4./30.;
  u =  0.;
  if (x(0) < xthr)
    {
      u(0) = gradx*x(0);
    }
  else
    {
      u(0) = gradx*xthr - gradx*(x(0)-xthr);
    }
}

void sol_exact4(const Vector &x, Vector &u)
{
  const double gradx = 1./3.;
  u =  0.;
  if (x(0) < xthr)
    {
      u(1) = gradx*x(0);
    }
  else
    {
      u(1) = gradx*xthr - gradx*(x(0)-xthr);
    }
}

void sol_exact5(const Vector &x, Vector &u)
{
  u =  0.;
}

void sol_exact6(const Vector &x, Vector &u)
{
  const double gradx = 1./3.;
  u =  0.;
  if (x(0) < xthr)
    {
      u(2) = gradx*x(0);
    }
  else
    {
      u(2) = gradx*xthr - gradx*(x(0)-xthr);
    }
}
