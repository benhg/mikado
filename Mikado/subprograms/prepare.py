#!/usr/bin/env python3
# coding: utf-8

"""
Subprogram that constitutes the first step of the Mikado pipeline.
"""

import sys
import os
import argparse
import logging
import logging.handlers
from ..utilities import path_join
from ..utilities.log_utils import formatter
from ..preparation.prepare import prepare
from ..configuration.configurator import to_json, check_json
from Mikado.exceptions import InvalidJson
import random


__author__ = 'Luca Venturini'


def setup(args):
    """Method to set up the analysis using the JSON configuration
    and the command line options.

    :param args: the ArgumentParser-derived namespace.
    """

    logger = logging.getLogger("prepare")
    logger.setLevel(logging.INFO)

    if args.start_method:
        args.json_conf["multiprocessing_method"] = args.start_method

    if args.output_dir is not None:
        args.json_conf["prepare"]["files"]["output_dir"] = getattr(args, "output_dir")

    if not os.path.exists(args.json_conf["prepare"]["files"]["output_dir"]):
        try:
            os.makedirs(args.json_conf["prepare"]["files"]["output_dir"])
        except (OSError, PermissionError) as exc:
            logger.error("Failed to create the output directory!")
            logger.exception(exc)
            raise
    elif not os.path.isdir(args.json_conf["prepare"]["files"]["output_dir"]):
        logger.error(
            "The specified output directory %s exists and is not a folder; aborting",
            args.json_conf["prepare"]["output_dir"])
        raise OSError("The specified output directory %s exists and is not a folder; aborting" %
                      args.json_conf["prepare"]["output_dir"])

    if args.log is not None:
        args.log.close()
        args.json_conf["prepare"]["files"]["log"] = args.log.name

    if args.seed is not None:
        args.json_conf["seed"] = args.seed
        random.seed(args.seed, version=2)

    if args.json_conf["prepare"]["files"]["log"]:
        try:
            _ = open(path_join(
                    args.json_conf["prepare"]["files"]["output_dir"],
                    os.path.basename(args.json_conf["prepare"]["files"]["log"])),
                "wt")
        except TypeError:
            raise TypeError((args.json_conf["prepare"]["files"]["output_dir"],
                    args.json_conf["prepare"]["files"]["log"]))

        handler = logging.FileHandler(
            path_join(
                args.json_conf["prepare"]["files"]["output_dir"],
                os.path.basename(args.json_conf["prepare"]["files"]["log"])),
            mode="wt")
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    while logger.handlers:
        logger.removeHandler(logger.handlers.pop())
    logger.addHandler(handler)
    assert logger.handlers == [handler]
    logger.propagate = False
    logger.info("Command line: %s",  " ".join(sys.argv))
    logger.info("Random seed: %s", args.json_conf["seed"])

    if args.verbose is True:
        args.json_conf["log_settings"]["log_level"] = "DEBUG"
    elif args.quiet is True:
        args.json_conf["log_settings"]["log_level"] = "WARN"

    args.level = args.json_conf["log_settings"]["log_level"]
    logger.setLevel(args.level)

    if args.list:

        args.json_conf["prepare"]["files"]["gff"] = []
        args.json_conf["prepare"]["files"]["labels"] = []
        args.json_conf["prepare"]["files"]["strand_specific_assemblies"] = []
        args.json_conf["prepare"]["files"]["source_score"] = dict()

        for line in args.list:
            fields = line.rstrip().split("\t")
            gff_name, label, stranded = fields[:3]
            if stranded not in ("True", "False"):
                raise ValueError("Malformed line for the list: {}".format(line))
            if gff_name in args.json_conf["prepare"]["files"]["gff"]:
                raise ValueError("Repeated prediction file: {}".format(line))
            elif label != '' and label in args.json_conf["prepare"]["files"]["labels"]:
                raise ValueError("Repeated label: {}".format(line))
            elif stranded not in ["False", "True"]:
                raise ValueError("Invalid strandedness value (must be False or True): {}".format(line))
            args.json_conf["prepare"]["files"]["gff"].append(gff_name)
            args.json_conf["prepare"]["files"]["labels"].append(label)
            if stranded == "True":
                args.json_conf["prepare"]["strand_specific_assemblies"].append(gff_name)
            if len(fields) > 3:
                try:
                    score = float(fields[3])
                except ValueError:
                    score = 0
                args.json_conf["prepare"]["files"]["source_score"][label] = score

    else:
        if args.gff:
            args.json_conf["prepare"]["files"]["gff"] = args.gff
        else:
            if not args.json_conf["prepare"]["files"]["gff"]:
                parser = prepare_parser()
                print(parser.format_help())
                sys.exit(0)
        if args.strand_specific is True:
            args.json_conf["prepare"]["strand_specific"] = True
        elif args.strand_specific_assemblies is not None:
            args.strand_specific_assemblies = args.strand_specific_assemblies.split(",")
            if len(args.strand_specific_assemblies) > len(args.json_conf["prepare"]["files"]["gff"]):
                raise ValueError("Incorrect number of strand-specific assemblies specified!")
            for member in args.strand_specific_assemblies:
                if member not in args.json_conf["prepare"]["files"]["gff"]:
                    raise ValueError("Incorrect assembly file specified as strand-specific")
            args.json_conf["prepare"]["strand_specific_assemblies"] = args.strand_specific_assemblies
        if args.labels:
            args.labels = args.labels.split(",")
            # Checks labels are unique
            assert len(set(args.labels)) == len(args.labels)
            assert not any([True for _ in args.labels if _.strip() == ''])
            if len(args.labels) != len(args.json_conf["prepare"]["files"]["gff"]):
                raise ValueError("Incorrect number of labels specified")
            args.json_conf["prepare"]["files"]["labels"] = args.labels
        else:
            if not args.json_conf["prepare"]["files"]["labels"]:
                args.labels = [""] * len(args.json_conf["prepare"]["files"]["gff"])
                args.json_conf["prepare"]["files"]["labels"] = args.labels

    for option in ["minimum_cdna_length", "procs", "single", "max_intron_length"]:
        if getattr(args, option) in (None, False):
            continue
        else:
            args.json_conf["prepare"][option] = getattr(args, option)

    for option in ["out", "out_fasta"]:
        if getattr(args, option) in (None, False):
            args.json_conf["prepare"]["files"][option] = os.path.basename(
                args.json_conf["prepare"]["files"][option]
            )
        else:
            args.json_conf["prepare"]["files"][option] = os.path.basename(getattr(args, option))

    if getattr(args, "fasta"):
        args.fasta.close()
        name = args.fasta.name
        if isinstance(name, bytes):
            name = name.decode()
        args.json_conf["reference"]["genome"] = name

    if isinstance(args.json_conf["reference"]["genome"], bytes):
        args.json_conf["reference"]["genome"] = args.json_conf["reference"]["genome"].decode()

    if args.keep_redundant is not None:
        args.json_conf["prepare"]["keep_redundant"] = args.keep_redundant

    if args.lenient is not None:
        args.json_conf["prepare"]["lenient"] = True

    if args.strip_cds is True:
        args.json_conf["prepare"]["strip_cds"] = True

    try:
        args.json_conf = check_json(args.json_conf)
    except InvalidJson as exc:
        logger.exception(exc)
        raise exc

    return args, logger


def prepare_launcher(args):

    args, logger = setup(args)
    try:
        prepare(args, logger)
        sys.exit(0)
    except Exception:
        raise


def prepare_parser():
    """
    This function defines the parser for the command line interface
    of the program.
    :return: an argparse.Namespace object
    :rtype: argparse.ArgumentParser
    """

    def to_cpu_count(string):
        """
        :param string: cpu requested
        :rtype: int
        """
        try:
            string = int(string)
        except:
            raise
        return max(1, string)

    def positive(string):
        """
        Simple function to return the absolute value of the integer of the input string.
        :param string:
        :return:
        """

        return abs(int(string))

    parser = argparse.ArgumentParser("""Script to prepare a GTF for the pipeline;
    it will perform the following operations:
    1- add the "transcript" feature
    2- sort by coordinates
    3- check the strand""")
    parser.add_argument("--fasta", type=argparse.FileType(),
                        help="Genome FASTA file. Required.")
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("-v", "--verbose", action="store_true", default=False)
    verbosity.add_argument("-q", "--quiet", action="store_true", default=False)
    parser.add_argument("--start-method", dest="start_method",
                        choices=["fork", "spawn", "forkserver"],
                        default=None, help="Multiprocessing start method.")
    strand = parser.add_mutually_exclusive_group()
    strand.add_argument("-s", "--strand-specific", dest="strand_specific",
                        action="store_true", default=False,
                        help="""Flag. If set, monoexonic transcripts
                        will be left on their strand rather than being
                        moved to the unknown strand.""")
    strand.add_argument("-sa", "--strand-specific-assemblies",
                        default=None,
                        type=str,
                        dest="strand_specific_assemblies",
                        help="Comma-delimited list of strand specific assemblies.")
    parser.add_argument("--list", type=argparse.FileType("r"),
                        help="""Tab-delimited file containing rows with the following format
                        <file>  <label> <strandedness> <score(optional)> <always_keep(optional)>""")
    parser.add_argument("-l", "--log", type=argparse.FileType("w"), default=None,
                        help="Log file. Optional.")
    parser.add_argument("--lenient", action="store_true", default=None,
                        help="""Flag. If set, transcripts with only non-canonical
                        splices will be output as well.""")
    parser.add_argument("-m", "--minimum-cdna-length", default=None, dest="minimum_cdna_length", type=positive,
                        help="Minimum length for transcripts. Default: 200 bps.")
    parser.add_argument("-MI", "--max-intron-size", default=None, type=positive, dest="max_intron_length",
                        help="Maximum intron length for transcripts. Default: 1,000,000 bps.")
    parser.add_argument("-p", "--procs",
                        help="Number of processors to use (default %(default)s)",
                        type=to_cpu_count, default=None)
    parser.add_argument("-scds", "--strip_cds", action="store_true", default=False,
                        help="Boolean flag. If set, ignores any CDS/UTR segment.")
    parser.add_argument("--labels", type=str, default="",
                        help="""Labels to attach to the IDs of the transcripts of the input files,
                        separated by comma.""")
    parser.add_argument("--single", action="store_true", default=False,
                        help="Disable multi-threading. Useful for debugging.")
    parser.add_argument("-od", "--output-dir", dest="output_dir",
                        type=str, default=None,
                        help="Output directory. Default: current working directory")
    parser.add_argument("-o", "--out", default=None,
                        help="Output file. Default: mikado_prepared.gtf.")
    parser.add_argument("-of", "--out_fasta", default=None,
                        help="Output file. Default: mikado_prepared.fasta.")
    parser.add_argument("--json-conf", dest="json_conf",
                        type=to_json, default="",
                        help="Configuration file.")
    parser.add_argument("-k", "--keep-redundant", default=None,
                        dest="keep_redundant", action="store_true",
                        help="Boolean flag. If invoked, Mikado prepare will retain redundant models.")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed number.")
    parser.add_argument("gff", help="Input GFF/GTF file(s).", nargs="*")
    parser.set_defaults(func=prepare_launcher)
    return parser
