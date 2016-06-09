# Registry Signature Searcher evaluation

This experiment runs via `make`.

First, to set up your environment:
* Run "`make SUBMODULES_CHECKED_OUT.log`" to initialize code submodules, which will include dependent-packages scripts.
* Run the appropriate dependent-packages script under the `deps` directory for your operating system.  It will recursively call other dependent-packages scripts for the submodules.
* Run "`make download-brown`", which will run the one download step that requires user interaction.
* Run `make -j $n`, where `$n` is the number of CPU cores you are willing to use for the experiment.

This workflow has been tested in Mac OS X.  On a machine with 16 cores, 16GBs RAM, 10Gb-attached storage, this experiment's run time is between several days and two weeks (wall clock time), and requires around 3TB of storage.  Note that on other platforms, other programs will need specification.  The script `run_on_osx.sh` gives a more self-documenting set of `make` calls, and `run_on_ubuntu.sh` translates some program calls.

Note that the primary `make` target (`dist`) will export the target files up two directories, working on the assumption that this directory is a Git submodule of the results repository.


## Alternate model construction

To run the Signature Searcher evaluation based on Registry differences as described in the dissertation section 5.4.3 ("Alternate difference basis for term sources"), run (with `$n` as described above):

    make -j $n alt-download
    ./run_on_osx.sh

This will perform the experiment like normal, except the Registry difference sets will be derived from a pre-computed differences file.
