#include "mfem.hpp"
#include <iostream>

using namespace mfem;

int main(int argc, char *argv[])
{
//    Mesh *mesh = new Mesh("../data/inline-tri.mesh", 1, 1);
//    Mesh *mesh = new Mesh("../data/inline-quad.mesh", 1, 1);
//    Mesh *mesh = new Mesh("../data/inline-tet.mesh", 1, 1);
   Mesh *mesh = new Mesh("../data/inline-hex.mesh", 1, 1);
   int dim = mesh->Dimension();

   for (int ref_levels = 0; ref_levels < 2; ref_levels++)
   {
      mesh->UniformRefinement();

      Array<int> edges, orientation;

      if (dim == 3)
         for(int i = 0; i<mesh->GetNFaces(); i++)
            mesh->GetFaceEdges(i, edges, orientation);
      else
         for(int i = 0; i<mesh->GetNEdges(); i++)
            mesh->GetEdgeVertices(i, edges);
   }

   delete mesh;

   return 0;
}