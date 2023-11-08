TEST_CASE("FaceEdgeConstraint",  "[Parallel], [NCMesh]")
{
   auto mesh = Mesh("../../data/ref-tetrahedron.mesh");

   REQUIRE(mesh.GetNE() == 1);
   {
      // Start the test with two tetrahedra attached by triangle.
      auto single_edge_refine = Array<Refinement>(1);
      single_edge_refine[0].index = 0;
      single_edge_refine[0].ref_type = Refinement::X;

      mesh.GeneralRefinement(single_edge_refine, 0); // conformal
   }

   REQUIRE(mesh.GetNE() == 2);
   mesh.EnsureNCMesh(true);

   auto partition = new int[mesh.GetNE()];
   partition[0] = 0;
   partition[1] = Mpi::WorldSize() > 1 ? 1 : 0;

   auto pmesh = ParMesh(MPI_COMM_WORLD, mesh, partition);

   Array<int> refines;
   if (Mpi::WorldRank() == 0)
   {
      refines.Append(0);
   }

   // Rank 0 uniform refines.
   pmesh.GeneralRefinement(refines, 1); // nonconformal

   REQUIRE(pmesh.GetGlobalNE() == 8 + 1);

   // Rank 0 has all but one element.
   for (int i = 0; i < pmesh.GetGlobalNE() - 1; ++i)
   {
      Array<int> refines;
      if (Mpi::WorldRank() == 0)
      {
         refines.Append(i);
      }

      ParMesh tmp(pmesh);
      tmp.GeneralRefinement(refines);

      REQUIRE(tmp.GetGlobalNE() == 1 + 8 - 1 + 8); // 16 elements

      // Loop over all the elements now on rank 0, and refine each of those.
      // This is sufficient to trigger an edge-face constraint. In particular
      // the (i,j) = (2,13) combination. Again, Rank 0 has all but one element.
      for (int j = 0; j < tmp.GetGlobalNE() - 1; ++j)
      {
         if (Mpi::WorldRank() == 0)
         {
            refines[0] = j;
         }
         ParMesh ttmp(tmp);
         ttmp.GeneralRefinement(refines);

         REQUIRE(ttmp.GetGlobalNE() == 1 + 8 - 1 + 8 - 1 + 8); // 23 elements
         ttmp.ExchangeFaceNbrData(); // <-- Here be dragons.
      }

      tmp.ExchangeFaceNbrData();
   }

   delete [] partition;
} // test case