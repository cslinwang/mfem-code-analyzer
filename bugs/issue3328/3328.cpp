SECTION("Test loading data with multiple underscores in directory name")
{
    // Create a directory with multiple underscores in the name
    std::string dir_name = "base_with_multiple_underscores";
    REQUIRE(mkdir(dir_name.c_str(), 0777) == 0);

    // Attempt to load data from the directory
    VisItDataCollection dc_test(dir_name);
    dc_test.Load(5);

    // Verify that the data was not loaded successfully
    REQUIRE(dc_test.GetMesh() == nullptr);
    REQUIRE(dc_test.GetField("u") == nullptr);
    // Add similar checks for other data you expect to be present

    // Clean up the test directory
    REQUIRE(rmdir(dir_name.c_str()) == 0);
}