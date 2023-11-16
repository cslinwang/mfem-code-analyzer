#include "mfem.hpp"

using namespace mfem;

int main(int argc, char *argv[])
{
   const char *mesh_file = "/root/mfem/mfem/data/star.mesh"; // invalid read from Valgrind
   // const char *mesh_file = "../data/fichera.mesh"; // no Valgrind errors

   int order = 3;
   int basis = BasisType::GetType('G');

   Mesh *mesh = new Mesh(mesh_file, 1, 1);
   Mesh *mesh_lor = new Mesh(mesh, order, basis);

   delete mesh;
   delete mesh_lor;

   return 0;
}