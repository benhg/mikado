# Version 1.5

**IMPORTANT**: this release fixes a bug ([#139](https://github.com/EI-CoreBioinformatics/mikado/issues/139)) whereupon cDNAs completely or partially in letters different from ATGCNn (eg. **lowercase**, ie ***soft-masked*** nucleotides) would not have been reversed-complemented correctly. Therefore, any run on soft-masked genomes with prior releases ***would be invalid***.

Users are ***very strongly recommended*** to update Mikado as soon as possible.

**IMPORTANT**: this release **changes the format of the mikado database**. As such, old mikado databases **have to be regenerated with Mikado serialise** in order for the run not to fail.

**IMPORTANT**: this release has completely overhauled the scoring files. We now provide only two ("plant.yaml" and "mammalian.yaml"). "Plant.yaml" should function also for insect or fungal species, but we have not tested it extensively. Old scoring files can be found under "HISTORIC".

Two of the major highlits of this release are:
  - the completion of the "padding" functionality. Briefly, if instructed to do so, now Mikado will be able to uniform the ends of transcripts within a single locus (similar to what was done for the last _Arabidopsis thaliana_ annotation release). The behaviour is controlled by the "pad" boolean switch, and by the "ts_max_splices" and "ts_distance" parameters under "pick". Please note that now "ts_distance" refers to the **transcriptomic** distance, ie, long introns are not considered for this purpose.
  - general improvements in speed and multiprocessing, as well as flexibility, for the Mikado compare utility.

With this release, we are also officially dropping support for Python 3.4. Python 3.5 will not be automatically tested for, as many Conda dependencies are not up-to-date, complicating the TRAVIS setup.

Bugfixes and improvements:

- Mikado has now been tested to be compatible with Python 3.7. Please note that if you are using Python 3.7, at the time of release, datrie [has to be installed manually](https://github.com/pytries/datrie/issues/52) **before** installing Snakemake.
- Mikado now always uses PySam, instead of PyFaidx, to fetch chromosomal regions (e.g. during prepare and pick). This speeds up and lightens the program, as well as making tests more manageable.
- Fixed a bug which caused some loci to crash at the last part of the picking stage
- Made logging more sensible and informative for all three steps of the pipeline (prepare, serialise, pick)
- For the external scores, Mikado can now accept any type of numerical or boolean value. Mikado will understand at serialisation time whether a particular score can be used raw (ie its values are strictly comprised between 0 and 1) or whether it has to be forcibly scaled.
  - This allows Mikado to use e.g. transcript expression as a valid metric.
- Now coding and non-coding transcripts will be in different loci.
- Dropped the by-now obsolete "nosetests" suite for testing, moving to the modern and maintained "pytest".
- Corrected a long-standing bug that made Mikado lose track of some fragments during the fragment removal phase. Somewhat confusingly, Mikado printed those loci into the output, but reported in the log file that there was a "missing locus". Now Mikado is able to correctly keeping track of them and removing them.
- Corrected a bug in the calculation of overlapping intervals during BLAST serialisation.
- Now BLAST HSPs will have stored as well whether there is an in-frame stop codon.
- Now Mikado pick will be forced to run in single-threaded mode if the user is asking for debugging-level logs. This is to prevent a [re-entrancy race condition that causes deadlocks](https://codewithoutrules.com/2017/08/16/concurrency-python/).
- Mikado prepare now can accept models that lack any exon features but still have valid CDS/UTR features - this is necessary for some protein prediction tools.
- Fixed [#124](https://github.com/EI-CoreBioinformatics/mikado/issues/124): Mikado was giving an error when trying to launch from a folder with an invalid "plants.yaml" file, due to not checking correctly the validity of the file itself.
- Fixed [#139](https://github.com/EI-CoreBioinformatics/mikado/issues/139): Mikado was reverse complementing non-uppercase letters incorrectly.
- [#135](https://github.com/EI-CoreBioinformatics/mikado/issues/135): Mikado so far operated under the assumption that the 8th field in GTF files was the **frame**, not the **phase** like in GFF3s. This is actually incompatible with EnsEMBL and many widespread tools such as [GenomeTools](http://genometools.org/) or [GffRead](https://github.com/gpertea/gffread). Starting from this version, Mikado uniforms with these other tools.
- Fixed [#34](https://github.com/EI-CoreBioinformatics/mikado/issues/34): now Mikado can specify a valid codon table among those provided by [NCBI  through BioPython](ftp://ftp.ncbi.nih.gov/entrez/misc/data/gc.prt). The default is "0", ie the Standard table but with only the canonical "ATG" being accepted as valid start codon.
- Fixed [#123](https://github.com/EI-CoreBioinformatics/mikado/issues/123): now add_transcript_to_feature.gtf automatically splits chimeric transcripts and corrects mistakes related the intron size.
- Fixed [#126](https://github.com/EI-CoreBioinformatics/mikado/issues/126): now reversing the strand of a model will cause its CDS to be stripped.
- Fixed [#127](https://github.com/EI-CoreBioinformatics/mikado/issues/127): previously, Mikado _prepare_ only considered cDNA coordinates when determining the redundancy of two models. In some edge cases, two models could be identical but have a different ORF called. Now Mikado will also consider the CDS before deciding whether to discard a model as redundant.
- [#130](https://github.com/EI-CoreBioinformatics/mikado/issues/130): it is now possible to specify a different metric inside the "filter" section of scoring.
- [#131](https://github.com/EI-CoreBioinformatics/mikado/issues/131): in rare instances, Mikado could have missed loci if they were lost between the sublocus and monosublocus stages. Now Mikado implements a basic backtracking recursive algorithm that should ensure no locus is missed.
- [#132](https://github.com/EI-CoreBioinformatics/mikado/issues/132),[#133](https://github.com/EI-CoreBioinformatics/mikado/issues/133): Mikado will now evaluate the CDS of transcripts during Mikado prepare.
- [#134](https://github.com/EI-CoreBioinformatics/mikado/issues/134): when checking for potential Alternative Splicing Events (ASEs), now Mikado will check whether the CDS phases are in frame with each other. Moreover, **Mikado will now calculate the CDS overlap percentage based on the primary transcript CDS length**, not the minimum CDS length between primary and candidate. Please note that the change **regarding the frame** also affects the monosublocus stage. Mikado still considers only the primary ORFs for the overlap.
- [#136](https://github.com/EI-CoreBioinformatics/mikado/issues/136): documentation has been updated to reflect the changes in the latest releases.
- [#137](https://github.com/EI-CoreBioinformatics/mikado/issues/137): unit-test coverage has been improved.
- [#138](https://github.com/EI-CoreBioinformatics/mikado/issues/138): Solved a bug which led Mikado to recalculate the phases for each model during picking, potentially creating mistakes for models truncated at the 5' end.
- [#141](https://github.com/EI-CoreBioinformatics/mikado/issues/141): During configure and prepare, Mikado can now flag some transcripts as coming from a "reference". Transcripts flagged like this **will never be modified nor dropped during a mikado prepare run**, unless generic or critical errors are registered. Moreover, if source scores are provided, Mikado will preferentially keep one identical transcript from those that have the highest *a priori* score. This will allow to e.g. prioritise PacBio or reference assemblies during prepare.
  - Please note that this change **does not affect the final picking**, but rather is just a mechanism for allowing Mikado to accept pass-through data.
  - If you desire to prioritise reference transcripts, please directly assign a source score higher than 0 to these sets.
- [#129](https://github.com/EI-CoreBioinformatics/mikado/issues/129): Mikado is now capable of correctly padding the transcripts so to uniform their ends in a single locus. This will also have the effect of trying to enlarge the ORF of a transcript if it is truncated to begin with.
- [#142](https://github.com/EI-CoreBioinformatics/mikado/issues/142): padded transcripts will add terminal *exons* rather than just extending their terminal ends. This should prevent the creation of faux retained introns. Moreover, now the padding procedure will explicitly find and discard transcripts that would become invalid after padding (e.g. because they end up with a far too long UTR, or retained introns). If some of the invalid transcripts had been used as template for the expansion, Mikado will remove the offending transcripts and restart the procedure.
  - As a consequence of fixing [#142](https://github.com/EI-CoreBioinformatics/mikado/issues/142), Transcript objects have been modified to expose the following methods related to the internal interval tree:
    - find/search (to find intersecting exonic or intronic intervals)
    - find_upstream (to find all intervals upstream of the requested one in the transcript)
    - find_downstream (to find all intervals downstream of the requested one in the transcript)
    - Moreover, transcript objects now do not have any more the unused "cds_introntree" property. Combined CDS and CDS introns are now present in the "cds_tree" object.
  - Again as a consequence of [#142](https://github.com/EI-CoreBioinformatics/mikado/issues/142), now Locus objects have a new private method - _swap_transcript - that allows two Transcript objects with the same ID to be exchanged within the locus. This is essential to allow the Locus to recalculate most scores and metrics (e.g. all the exons or introns in the locus).
 - [#148](https://github.com/EI-CoreBioinformatics/mikado/issues/148): during the pick phase, "reference" transcripts will never be excluded because they do not pass the minimum requirements set in the scoring file.
 - [#149](https://github.com/EI-CoreBioinformatics/mikado/issues/149): Now Mikado also provides a Docker file and a Singularity recipe, for ease of installation.
 - [#153](https://github.com/EI-CoreBioinformatics/mikado/issues/153): General speed improvements due to modifications in the Transcript class.
 - [#166](https://github.com/EI-CoreBioinformatics/mikado/issues/166): Mikado compare has been greatly improved, with the addition of:
	- proper multiprocessing
	- faster startup times
	- possibility of considering "fuzzy matches" for the introns. This means that two transcripts might be considered as a "match" even if their introns are slightly staggered. This helps e.g. when assessing imperfect data such as Nanopore, where the experimenter usually knows that the per-base precision is quite low.
	- the index has been modified, so that now gene objects are stored as [msgpack](https://github.com/msgpack/msgpack-python) json dumps rather than pure strings. This should make the indices smaller and faster to load.

# Version 1.2.4

Enhancement release. Following version 1.2.3, now Mikado can accept BED12 files as input for convert, compare and stats (see [#122](https://github.com/EI-CoreBioinformatics/mikado/issues/122)). This is becoming necessary as many long-reads alignment tools are preferentially outputting (or can be easily converted to) this format.

# Version 1.2.3

Mainly this is a bug fix release. It has a key advancement though, as now Mikado can accept BED12 files as input assemblies. This makes it compatible with Minimap2 PAF > BED12 system.

# Version 1.2.2

Minor bugfixes:
- Now Daijin should handle correctly the lack of DRMAA
- Now Dajin should treat correctly single-end short reads

# Version 1.2.1

Highlights for this version:

- The version of the algorithm for retained introns introduced in 1.1 was too stringent compared to previous versions. The code has been updated so that the new version of Mikado will produce results comparable to those of versions 1 and earlier. **ALL MIKADO USERS ARE ADVISED TO UPDATE THE SOFTWARE**.
- Daijin now supports Scallop.
- Now Mikado will print out also the alias in the final picking tables, to simplify lookup of final Mikado models with their original assembly (previously, the table for the .loci only contained the Mikado ID).
- Various changes on the BED12 internal representation. Now Mikado can also convert a genomic BED12 into a transcriptomic BED12.
- Updated the documentation, including a tutorial on how to create scoring files, and how to adapt Daijin to different user cases.
- Now finalised transcripts will always contain a dictionary containing the phases of the various CDS exons.
- Mikado prepare now will always reverse the strand for mixed-splicing events.
- Added unit-tests to keep in check the regression in calling retained introns, and for the new BED12 features.
- Minor bugfixes.


# Version 1.1 - "Prodigal"

Highlights for this release are the swithing by default to Prodigal in lieu of TransDecoder and to DIAMOND instead of NCBI BLASTX. The rationale behind the change is that the two former default programs scale poorly with the size of datasets, as neither was designed to maintain a good execution speed with potentially million sequences. Prodigal and DIAMOND fare much better with big datasets, and do speed up significantly the execution of the whole Daijin pipeline.

Changes in this release:

- Mikado is now compatible with NetworkX v. 2x.
- Mikado now accepts ORFs calculated by Prodigal, in GFF3 format, instead of only those by TransDecoder in BED format.
- Mikado compare indices now are **SQLite3 databases**, not compressed JSON files as in previous versions. This should allows for a faster loading and potentially, down the line, the chance to parallelise compare.
- By default, Daijin now uses **Prodigal and DIAMOND** instead of TransDecoder and BLAST. This should lead to massive speed-ups during the pipeline, although at the cost of slightly reduced accuracy.
- Improved the algorithm for finding retained introns, using a graph structure instead of potentially checking against every other transcript in the locus.
- Mikado configure now has a new flag, "--daijin", which instructs the program to create a Daijin-compatible configuration file, rather than a Mikado-only one.
- Fixed some bugs in Daijin regarding the handling of Long Reads.
- Fixed a bug in Daijin regarding the calculation of Trinity parameters - previously, Daijin could potentially ask Trinity for parameters for N times, where N is the number of required assemblies, lengthening the startup time.
- Solved a bug that created incompatibility with BioPython >= 1.69
- Solved some bugs that prevented Daijin from functioning correctly on a local computer
- Now Daijin by default recovers the information to load external software from an external configuration file. This allows for having a standard configuration file for external programs, without having to modify the main configuration all the time.
- Now Daijin creates and/or load a standard configuration file for the cluster, "daijin_hpc.yaml".

# Version 1.0.1

BugFix release.

- Fixed a bug which caused Mikado to go out of memory with very dense loci, when calculating the AS events.
- Fixed a bug which caused the log not to be saved correctly during the indexing for Mikado compare.
- Fixed a bug which caused Mikado pick to crash at the end, on rare cases.
- Data to be transmitted to picking process children is now stored in a temporary SQLITE3 database, to lessen memory usage and queue hangups.
- Fixed a bug while that caused a crash while Mikado was trying to approximate complex loci.
- Switched away from using clique-based algorithms, as they tend to be very memory intensive.

# Version 1.0

Changes in this release:

- **MAJOR**: solved a bug which caused a failure of clustering into loci in rare occasions. Through the graph clustering, now Mikado is guaranteed to group monoloci correctly.
- **MAJOR**: When looking for fragments, now Mikado will consider transcripts without a strand as being on the **opposite** strand of neighbouring transcripts. This prevents many monoexonic, non-coding fragments from being retained in the final output.
- **MAJOR**: now Mikado serialise also stores the ***frame*** information of transcripts. Hits on the opposite strand will be **ignored**. This requires to **regenerate all Mikado databases**.
- **MAJOR**: Added the final configuration files used for the article.
- Added three new metrics, "blast_target_coverage", "blast_query_coverage", "blast_identity"
- Changed the *default* repertoire of valid AS events to J, j, G, h (removed C and g).
- **Bug fix**: now Mikado will consider the cDNA/CDS overlap also for monoexonic transcripts, even when the "simple_overlap_for_monoexonic_loci" flag is set to true.
- Solved some issues with the Daijin schemas, which prevented correct referencing.
- Bug fix for finding retained introns - Mikado was not accounting for cases where an exon started within an intron and crossed multiple subsequent junctions.
- BF: Loci will never purge transcripts
- After creating the final loci, now Mikado will check for, and remove, any AS event transcript which would cross into the AS event.

# Version 1.0.0beta10

Changes in this release:

- **MAJOR**: re-written the clustering algorithm for the MonosublocusHolder stage. Now a holder will accept another monosublocus if:
    - the cDNA and CDS overlap is over a user-specified threshold
    *OR* 
    - there is some intronic overlap
    *OR*
    - one intron of either transcript is completely contained within an exon of the other.
    *OR*
    - at least one of the transcripts is monoexonic and there is some overlap of any kind. This behaviour (which was the default until this release) can be switched off through pick/clustering/simple_overlap_for_monoexonic (default true).
- **MAJOR**: changed slightly the anatomy of the configuration files. Now "pick" has two new subsections, "clustering" and "fragments".
    - Clustering: dedicated to how to cluster the transcripts in the different steps. Currently it contains the keys:
        - "flank"
        - "min_cdna_overlap" and "min_cds_overlap" (for the second clustering during the monosublocusHolder phase)
        - "cds_only": to indicate whether we should only consider the CDS for clustering after the initial merging in the Superlocus.
        - "simple_overlap_for_monoexonic": to switch on/off the old default behaviour with monoexonic transcripts
        - "purge": whether to completely exclude failed loci, previously under "run_options"
    - Fragments: dedicated to how to identify and treat putative fragments. Currently it contains the keys:
        - "remove": whether to exclude fragments, previously under "run_options"
        - "valid_class_codes": which class codes constitute a fragment match. Only class codes in the "Intronic", "Overlap" (inclusive of _) and "Fragment" categories are allowed.
        - max_distance: for non-overlapping fragments (ie p and P), maximum distance from the gene.
- Solved a long-standing bug which caused Mikado compare to consider as fusion also hits on the opposite strand only.
- Mikado compare now also provides the location of the matches in TMAP and REFMAP files.
- Introduced a new utility, "class_codes", to print out the information of the class codes. The definition of class codes is now contained in a subpackage of "scales".
- The "metrics" utility now allows for interactive querying based on category or metric name.
- The class code repertoire for putative fragments has been expanded, and made configurable through the "fragments" section.
- When printing out putative fragments, now Mikado will indicate the class code of the fragment, the match against which it was deemed a fragment of, and the distance of said fragment (if they are not overlapping). 
- Deprecated the "discard_definition" flag in Mikado serialise. Now Mikado will infer on its own whether to use the definition or the ID for serialising BLAST results.
- Now AbstractLocus implementations have a private method to check the correctness of the json_conf. As a corollary, Transcript and children have been moved to their own subpackage ("transcripts") in order to break the circular dependency Mikado.loci.Abstractlocus <- Mikado.configurator <- Mikado.loci.Transcript. *Technical note*: checking the consinstency of the configuration is an expensive operation, so it will be executed on demand rather than automatically.
- The methods to calculate scores and metrics have been moved to the AbstractLocus class, so to minimize the incidence of bugs due to code duplication and diversion.
- Made the checks for the scoring files more robust.
- Re-written the "find_retained_introns" method of AbstractLocus, to solve some bugs found during the utilisation of last beta. As a corollary, expanded the intervaltree module to allow searches for "tagged" intervals.
- Now the "monoloci_out" files contain the Monosublocus**Holder** step, not the Monosublocus step. This should help during fine-tuning. 
- Minimal requirements for alternative splicing events are now specified with a syntax analogous to that of minimal requirements, and that for not considering a locus as a putative fragment, under the tag "as_requirements".
- Fixed a bug which caused transcript requirements to be ignored if pick/clustering/purge was set to False.
- Mikado now supports also Python3.6.


# Version 1.0.0beta9 - "External scores"

Changes in this release:

- Mikado prepare, stats and compare are capable of using GFFs with "match/match_part" or "cDNA_match" features as input. This allows eg. to obtain sensible statistics for the alignments of Trinity transfrags or long reads when using GMAP inside Daijin.
- When the option "subloci_from_cds_only" is set to true (or the equivalent command line switch is invoked), AS events class codes will be calculated on the coding portion only of the transcript.
- Mikado now allows to perform unittest on the installed module, through the function "Mikado.test". This is simply a wrapper to NoseTest, through a call to the numpy tester.	
- **IMPORTANT**: in strand-specific mode, now Mikado prepare will not flip transcripts which have been misassigned to the opposite strand. Those transcripts will be kept on the original strand, and tagged.
- **IMPORTANT**: now Mikado will use all the verified introns found in a **Superlocus** to determine the fraction of verified introns per locus in each transcript. At the stage of Locus, ie creation of genes, this will revert to check only the verified introns in the locus. Also, solved a bug related to this metric.
- **IMPORTANT**: at the stage of the creation of monosubloci-holders, now Mikado groups together also transcripts **for which at least one intron is completely contained within the exon of another**. This should solve spurious cases where we called multiple loci instead of one, while probably avoiding trans-splicing.
- **IMPORTANT**: otionally now Mikado can perform the second clustering of transcripts based on simple overlap (either of the CDS or of all exonic features). The option can be invoked from the command line. 
- Two new metrics:
  - "suspicious_splicing" will allow to identify transcripts with mixed_splices, or which would have at least one canonical intron if moved to the opposite strand.
  - "only_non_canonical_splicing" will allow to identify transcripts whose splicing sites are all non-canonical.
- It is now possible to give Mikado a tab-delimited file of pre-calculated metrics (which must be numeric), during serialise. The file should have the transcript ids in the first column and have a header as first line; this header must have "TID" as first field, and no repeated fields afterwards. External metrics can be specified in the scoring configuration using the syntax "external.{name of the score}". If an inexistent metric is asked for, Mikado will assign a default value of 0 to it.
- It is now possible to use metrics with values between 0 and 1, inclusive directly as scoring, by specifying the parameter "use_raw: True". This is available only for metrics which have been tagged as being "usable raw", or with externally provided metrics. The option is valid only when looking for the maximum or minimum value for a metric, not when looking for a target. If an incorrect configuration is specified, Mikado will crash.
- Mikado prepare in "lenient" mode will keep also transcripts with a mixture of strands for the splicing junctions. Such transcripts are marked with the "suspicious_splicing" GTF attribute.
- Mikado prepare can be asked to keep all transcripts, even if they are redundant. The new behaviour (disabled by default) is switched on by the boolean parameter "prepare/keep_redundant".
- Mikado pick can consider transcripts with CDS ending within a CDS intron as truncated due to a retained intron event. This potentially allows Mikado to detect retained introns even when only CDSs are provided. The behaviour is disabled by default, and can be switched on using the boolean configuration parameter "pick/run_options/consider_truncated_for_retained".
- Some bugs have been detected and solved thanks to the collaboration with Hugo Darras.
- Many tests, including system ones, have been added to the test suite. Tests have been fixed for Python3.4 as well.

# Version 1.0.0beta7.2

Mainly fixes for Daijin, in order to be able to handle different versions of Trinity, GMAP and PortCullis.

# Version 1.0.0beta7.1

BugFix release:

- Corrected a bug identified by Hugo Darras, whereby Mikado crashed when asked not to report alternative splicing events
- Mikado compare now supports compressing the outputs
- Bug fix for Mikado util stats - now it functions also when exonic features contain "derived_from" tags
- Bug fix for bam2gtf.py

# Version 1.0.0beta7 - "Storing the stacks"

Changes:

- Now we use ujson and SQLite to store out-of-memory the data loaded during the "prepare" step, massively reducing the memory needed for this step.
- TransDecoder is now optional in the Daijin pipeline
- Mikado can be instructed to pad transcripts at their ends, to make all transcripts at a locus compatible in terms of their ends (eventually extended the CDS, if possible). The protocol was inspired by the AtRTD2 release: http://biorxiv.org/content/early/2016/05/06/051938

# Version 1.0.0beta6

Beta 6, Hopefully final release for the article. Highlights:

- Compatibility with DIAMOND
- Essential bugfix for handling correctly verified introns
- Updated scoring files

# Version 1.0.0beta5

First public release of Mikado.

Changelog:

- Added a flank option in Daijin
- Documentation ready, inclusive of a tutorial for Daijin itself
- Bug fixes, especially to Daijin

# Version 1.0.0beta4

Changelog:

- Daijin now has a proper schema and a proper configure command. Still to implement: schema check on starting Daijin itself
- Documentation is now more complete (see eg sections on Compare and Configuration)
- Now mo and O have been renamed to g and G respectively

# Version 1.0.0beta3

Changelog:

- Solved a bug which prevented correct loading of ORFs in monoexonic transcripts with an ORF on the negative strand
- Dagger is now daijin
- Added controls in Daijin for:
    - Minimum length of TD ORFs
    - rerun from a particular target
- Minor polishes to command line interfaces and the like.

# Version 1.0.0beta2

Changes:

- Small bug fixes for DAGGER
- Introduced a very basic configuration utility for DAGGER
- Now Mikado programs have a sensible help message, including description.

# Version 1.0.0beta1

Finally almost ready! Major changes:

- mikado is now completely integrated with DAGGER, h/t Daniel Mapleson
- Both mikado and dagger are called as "mikado" and "dagger", without any trailing ".py"
- We are now in feature freeze, with the exception of dagger.

# Version 0.24.0 "Blade sharpening"

This release is mainly focused on two aims: integration with Dagger, and the possibility of performing a good self-comparison with mikado.py compare.

Detailed changes for the release:

- scoring files are now inside a proper subfolder, and can be copied during configuration, for user modification
- the configuration process has now been widely rehauled, together with the configuration files, to make Mikado compatible with DAGGER
- Introduced a functioning deep copy method for gene objects
- Now redundant adding of exons into a transcript object will not throw an exception but will be silently ignored
- Mikado parsers now support GZIPped and BZIPped files, through python-magic
- added the possibility of specifying which subset of input assemblies are strand-specific during the preparation step
- configure and prepare now accept a tab-separated text file (format: , ) as input
- compare now can perform two types of self-analysis:
    - "internal", which outputs only a tmap file and performs a comparison all-vs-all within each multi-isoform gene locus
    - "self", in which each transcript is analysed as it would during a normal run, but removing itself from the reference.
- Now serialise can accept FASTA references, pyFaidx is used to recover the correct FAI
- pick and configure can now specify the mode of action (nosplit, split, stringent, lenient, permissive) by CL instead of having to modify the configuration file
- cleaned up the sample_data directory, plus now the configuration file is created on the spot by Snakemake (ensuring compatibility with the latest version)

# Version 0.23.2 "Stats bugfix"

Changes for this micro release:

- Bug fixes for some debug log messages
- Bug fixes for the stats utility
- added the flank option for mikado

# Version 0.23.1 "Faster stats"

Changes:

- Stats is now much faster and lighter, as objects are discarded upon analysis, not kept around for the whole run duration
- Pick now preferentially outputs only one ORF per transcript, behaviour regulated by pick/output_format/report_all_orfs
- BugFix for the detection of fragments during pick

# Version 0.23.0 "Clap-o-meter"

New features:

- Added a converter for (GTF <=> GFF3) > BED12 conversions in mikado.py util convert
- Now it is possible to provide a predefined malus/bonus to transcripts according to their sources using the following syntax in the configuration file:

        pick:
          source_score:
            source1: score1
            source2: score
            ...

It is generally *not* advised to use such an option unless the user really wants to emphasize or penalise a particular set of transcripts, eg. those coming from PacBio data.

# Version 0.22.0 "FastXML"

Transitioned the XML parser to the experimental Bio.SearchIO module, which uses internally C-level APIs and is therefore twice as fast than the canonical implementation. This required some rewriting at the class level in Mikado and a cloning of the original class to make it a proper iterative class.
Moreover, now requirements for the scoring can accept also eg boolean values.

# Version 0.21.0 "Trim galore"

Major changes for this release:

- Trim is now functioning
- ORFs from transdecoder are treated correctly - even truncated and internal ones. No more faux UTRs!
- Changes in the DB structure to accomodate the ORF information - note, this means that the databases have to be regenerated

