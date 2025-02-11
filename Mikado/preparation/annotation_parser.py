import multiprocessing
from ..parsers import to_gff
from ..utilities.log_utils import create_queue_logger
import logging
import logging.handlers
from .. import exceptions
from sys import intern
try:
    import ujson as json
except ImportError:
    import json
import sqlite3
import os
# from ..parsers.bed12 import BED12
from ..transcripts import Transcript
from operator import itemgetter


__author__ = 'Luca Venturini'


class AnnotationParser(multiprocessing.Process):

    def __init__(self,
                 submission_queue,
                 logging_queue,
                 identifier,
                 min_length=0,
                 max_intron=3*10**5,
                 log_level="WARNING",
                 strip_cds=False):

        super().__init__()
        self.submission_queue = submission_queue
        self.min_length = min_length
        self.max_intron = max_intron
        self.__strip_cds = strip_cds
        self.logging_queue = logging_queue
        self.log_level = log_level
        self.__identifier = identifier
        self.name = "AnnotationParser-{0}".format(self.identifier)
        self.logger = None
        self.handler = None
        self.logger = logging.getLogger(self.name)
        create_queue_logger(self, prefix="prepare")
        # self.logger.warning("Started process %s", self.name)

    def __getstate__(self):

        state = self.__dict__.copy()
        for key in ("logger", "handler", "_log_handler"):
            if key in state:
                del state[key]

        return state

    def __setstate__(self, state):

        self.__dict__.update(state)
        create_queue_logger(self)

    def run(self):

        found_ids = set()
        self.logger.debug("Starting to listen to the queue")
        counter = 0
        while True:
            results = self.submission_queue.get()
            try:
                label, handle, strand_specific, is_reference, shelf_name = results
            except ValueError as exc:
                raise ValueError("{}.\tValues: {}".format(exc, ", ".join([str(_) for _ in results])))
            if handle == "EXIT":
                self.submission_queue.put(("EXIT", "EXIT", "EXIT", "EXIT", "EXIT"))
                break
            counter += 1
            self.logger.debug("Received %s (label: %s; SS: %s, shelf_name: %s)",
                              handle,
                              label,
                              strand_specific,
                              shelf_name)
            try:
                gff_handle = to_gff(handle)
                if gff_handle.__annot_type__ == "gff3":
                    new_ids = load_from_gff(shelf_name,
                                            gff_handle,
                                            label,
                                            found_ids,
                                            self.logger,
                                            min_length=self.min_length,
                                            max_intron=self.max_intron,
                                            strip_cds=self.__strip_cds,
                                            is_reference=is_reference,
                                            strand_specific=strand_specific)
                elif gff_handle.__annot_type__ == "gtf":
                    new_ids = load_from_gtf(shelf_name,
                                            gff_handle,
                                            label,
                                            found_ids,
                                            self.logger,
                                            min_length=self.min_length,
                                            max_intron=self.max_intron,
                                            is_reference=is_reference,
                                            strip_cds=self.__strip_cds,
                                            strand_specific=strand_specific)
                elif gff_handle.__annot_type__ == "bed12":
                    new_ids = load_from_bed12(shelf_name,
                                              gff_handle,
                                              label,
                                              found_ids,
                                              self.logger,
                                              is_reference=is_reference,
                                              min_length=self.min_length,
                                              max_intron=self.max_intron,
                                              strip_cds=self.__strip_cds,
                                              strand_specific=strand_specific)
                else:
                    raise ValueError("Invalid file type: {}".format(gff_handle.name))

                if len(new_ids) == 0:
                    raise exceptions.InvalidAssembly(
                        "No valid transcripts found in {0}{1}!".format(
                            handle, " (label: {0})".format(label) if label != "" else ""
                        ))

            except exceptions.InvalidAssembly as exc:
                self.logger.exception(exc)
                continue
            except Exception as exc:
                self.logger.exception(exc)
                raise

        self.logger.debug("Sending %s back, exiting.", counter)

    @property
    def identifier(self):
        """
        A numeric value that identifies the process uniquely.
        :return:
        """
        return self.__identifier


def __raise_redundant(row_id, name, label):

    if label == '':

        raise exceptions.RedundantNames(
            """{0} has already been found in another file but is present in {1};
               this will cause unsolvable collisions. Please rerun preparation using
               labels to tag each file.""".format(
                row_id, name
            ))
    else:
        raise exceptions.RedundantNames(
            """"{0} has already been found in another file but is present in {1};
            this will cause unsolvable collisions. This happened even if
            you specified label {2}; please change them in order to ensure that
            no collisions happen.""".format(row_id, name, label))


def __raise_invalid(row_id, name, label):

    raise exceptions.InvalidAssembly(
        """{0} is present multiple times in {1}{2}. This breaks the input parsing.
        Please ensure that the file is properly formatted, with unique IDs.""".format(
            row_id,
            name,
            "(label: {0})".format(label) if label != '' else ""))


def load_into_storage(shelf_name, exon_lines, min_length, logger, strip_cds=True, max_intron=3*10**5):

    """Function to load the exon_lines dictionary into the temporary storage."""

    conn = sqlite3.connect(shelf_name)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "CREATE TABLE dump (chrom text, start integer, end integer, strand text, tid text, features blob)")
    except sqlite3.OperationalError:
        # Table already exists
        logger.error("Shelf %s already exists (maybe from a previous aborted run?), dropping its contents", shelf_name)
        cursor.close()
        conn.close()
        os.remove(shelf_name)
        conn = sqlite3.connect(shelf_name)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE dump (chrom text, start integer, end integer, strand text, tid text, features blob)")

    cursor.execute("CREATE INDEX idx ON dump (tid)")
    logger.debug("Created tables for shelf %s", shelf_name)

    for tid in exon_lines:
        if "features" not in exon_lines[tid]:
            raise KeyError("{0}: {1}\n{2}".format(tid, "features", exon_lines[tid]))
        if ("exon" not in exon_lines[tid]["features"] or
                len(exon_lines[tid]["features"]["exon"]) == 0):
            # Match-like things
            if "match" in exon_lines[tid]["features"]:
                if len(exon_lines[tid]["features"]["match"]) > 1:
                    logger.warning("Invalid features for %s, skipping.", tid)
                    continue
                exon_lines[tid]["features"]["exon"] = [exon_lines[tid]["features"]["match"][0]]
                logger.warning("Inferring that %s is a mono-exonic transcript-match: (%s, %d-%d)",
                               tid, exon_lines[tid]["chrom"],
                               exon_lines[tid]["features"]["exon"][0][0],
                               exon_lines[tid]["features"]["exon"][0][1])
                del exon_lines[tid]["features"]["match"]
            elif (strip_cds is False and "CDS" in exon_lines[tid]["features"] and
                len(exon_lines[tid]["features"]["CDS"]) > 0):
                pass
            else:
                logger.warning("No valid exon feature for %s, continuing", tid)
                continue
        elif "match" in exon_lines[tid]["features"] and "exon" in exon_lines[tid]["features"]:
            del exon_lines[tid]["features"]["match"]

        if "exon" in exon_lines[tid]["features"]:
            segments = exon_lines[tid]["features"]["exon"][:]
        elif "CDS" in exon_lines[tid]["features"]:
            segments = exon_lines[tid]["features"]["CDS"][:]
            for feature in exon_lines[tid]["features"]:
                if "utr" in feature.lower():
                    segments.extend(exon_lines[tid]["features"][feature])
                else:
                    continue
            segments = sorted(segments, key=itemgetter(0))
            # Now check the exons
            exons = []
            if len(segments) == 0:
                logger.warning("No valid exon feature for %s, continuing", tid)
                continue
            elif len(segments) == 1:
                exons = segments[0]
            else:
                current = segments[0]
                for pos in range(1, len(segments)):
                    segment = segments[pos]
                    if segment[0] > current[1] + 1:
                        exons.append(current)
                        current = segment
                    elif segment[0] == current[1] + 1:
                        current = (current[0], segment[1], None)
                    else:
                        logger.warning("Overlapping segments found in %s. Discarding it", tid)
                        continue
                exons.append(current)
            exon_lines[tid]["features"]["exon"] = exons[:]
        else:
            raise KeyError(exon_lines[tid]["features"])

        segments = sorted(segments, key=itemgetter(0))
        tlength = 0
        start, end = segments[0][0], segments[-1][1]
        biggest_intron = -1
        num_segments = len(segments)
        for pos, segment in enumerate(segments):
            if pos < num_segments - 1:
                later = segments[pos + 1]
                biggest_intron = max(biggest_intron,
                                     later[0] - (segment[1] + 1))
            tlength += segment[1] + 1 - segment[0]

        # Discard transcript under a certain size
        if tlength < min_length:
            if exon_lines[tid]["is_reference"] is True:
                logger.info("%s retained even if it is too short (%d) as it is a reference transcript.",
                            tid, tlength)
            else:
                logger.info("Discarding %s because its size (%d) is under the minimum of %d",
                             tid, tlength, min_length)
                continue

        # Discard transcripts with introns over the limit
        if biggest_intron > max(-1, max_intron):
            if exon_lines[tid]["is_reference"] is True:
                logger.info(
                    "%s retained even if its longest intron is over the limit (%d) as it is a reference transcript.",
                    tid, biggest_intron)
            else:
                logger.info("Discarding %s because its longest intron (%d) is over the maximum of %d",
                             tid, biggest_intron, max_intron)
                continue

        values = json.dumps(exon_lines[tid])

        logger.debug("Inserting %s into shelf %s", tid, shelf_name)
        cursor.execute("INSERT INTO dump VALUES (?, ?, ?, ?, ?, ?)", (exon_lines[tid]["chrom"],
                                                                      start,
                                                                      end,
                                                                      exon_lines[tid]["strand"],
                                                                      tid,
                                                                      values))

    cursor.close()
    conn.commit()
    conn.close()
    return


def load_from_gff(shelf_name,
                  gff_handle,
                  label,
                  found_ids,
                  logger,
                  min_length=0,
                  max_intron=3*10**5,
                  is_reference=False,
                  strip_cds=False,
                  strand_specific=False):
    """
    Method to load the exon lines from GFF3 files.
    :param shelf_name: the name of the shelf DB to use.
    :param gff_handle: The handle for the GTF to be parsed.
    :param label: label to be attached to all transcripts.
    :type label: str
    :param found_ids: set of IDs already found in other files.
    :type found_ids: set
    :param logger: a logger to be used to pass messages
    :type logger: logging.Logger
    :param min_length: minimum length for a cDNA to be considered as valid
    :type min_length: int
    :param max_intron: maximum intron length for a cDNA to be considered as valid
    :type max_intron: int
    :param strip_cds: boolean flag. If true, all CDS lines will be ignored.
    :type strip_cds: bool
    :param strand_specific: whether the assembly is strand-specific or not.
    :type strand_specific: bool
    :param is_reference: boolean. If set to True, the transcript will always be retained.
    :type is_reference: bool
    :return:
    """

    exon_lines = dict()

    strip_cds = strip_cds and (not is_reference)
    strand_specific = strand_specific or is_reference

    transcript2genes = dict()
    new_ids = set()

    to_ignore = set()

    for row in gff_handle:
        if row.feature == "protein":
            continue
        elif row.is_transcript is True or row.feature == "match":
            if label != '':
                row.id = "{0}_{1}".format(label, row.id)
                row.source = label
            if row.id in found_ids:
                __raise_redundant(row.id, gff_handle.name, label)
            elif row.id in exon_lines:
                # This might sometimes happen in GMAP
                logger.warning(
                    "Multiple instance of %s found, skipping any subsequent entry",
                    row.id)
                to_ignore.add(row.id)
                continue
            #
            # if row.id not in exon_lines:
            exon_lines[row.id] = dict()
            exon_lines[row.id]["source"] = row.source
            if row.parent:
                transcript2genes[row.id] = row.parent[0]
            else:
                transcript2genes[row.id] = row.id
            assert row.id is not None
            if row.id in found_ids:
                __raise_redundant(row.id, gff_handle.name, label)

            exon_lines[row.id]["attributes"] = row.attributes.copy()
            exon_lines[row.id]["chrom"] = row.chrom
            exon_lines[row.id]["strand"] = row.strand
            exon_lines[row.id]["tid"] = row.transcript or row.id
            exon_lines[row.id]["parent"] = "{}.gene".format(row.id)
            exon_lines[row.id]["features"] = dict()
            # Here we have to add the match feature as an exon, in case it is the only one present
            if row.feature == "match":
                exon_lines[row.id]["features"][row.feature] = []
                exon_lines[row.id]["features"][row.feature].append((row.start, row.end, row.phase))

            exon_lines[row.id]["strand_specific"] = strand_specific
            exon_lines[row.id]["is_reference"] = is_reference
            continue
        elif row.is_exon is True:
            if not row.is_cds or (row.is_cds is True and strip_cds is False):
                if len(row.parent) == 0 and "cDNA_match" == row.feature:
                    if label == '':
                        __tid = row.id
                    else:
                        __tid = "{0}_{1}".format(label, row.id)
                    row.parent = __tid
                    transcript2genes[__tid] = "{}_match".format(__tid)
                    row.feature = "exon"
                elif row.feature == "match_part":
                    if label == '':
                        __tid = row.parent[0]
                    else:
                        __tid = "{0}_{1}".format(label, row.parent[0])
                    row.parent = __tid
                    transcript2genes[__tid] = "{}_match".format(__tid)
                    row.feature = "exon"

                elif label != '':
                    row.transcript = ["{0}_{1}".format(label, tid) for tid in row.transcript]

                parents = row.transcript[:]
                for tid in parents:

                    if tid in found_ids:
                        __raise_redundant(tid, gff_handle.name, label)
                    elif tid in to_ignore:
                        continue
                    if tid not in exon_lines and tid in transcript2genes:
                        exon_lines[tid] = dict()
                        exon_lines[tid]["attributes"] = row.attributes.copy()
                        if label:
                            exon_lines[tid]["source"] = label
                        else:
                            exon_lines[tid]["source"] = row.source
                        exon_lines[tid]["chrom"] = row.chrom
                        exon_lines[tid]["strand"] = row.strand
                        exon_lines[tid]["features"] = dict()
                        exon_lines[tid]["tid"] = tid
                        exon_lines[tid]["parent"] = transcript2genes[tid]
                        exon_lines[tid]["strand_specific"] = strand_specific
                        exon_lines[tid]["is_reference"] = is_reference
                    elif tid not in exon_lines and tid not in transcript2genes:
                        continue
                    else:
                        if "exon_number" in row.attributes:
                            del row.attributes["exon_number"]
                        if (exon_lines[tid]["chrom"] != row.chrom or
                                exon_lines[tid]["strand"] != row.strand):
                            __raise_invalid(tid, gff_handle.name, label)
                        exon_lines[tid]["attributes"].update(row.attributes)

                    if row.feature not in exon_lines[tid]["features"]:
                        exon_lines[tid]["features"][row.feature] = []
                    exon_lines[tid]["features"][row.feature].append((row.start, row.end, row.phase))
                    new_ids.add(tid)

            else:
                continue
    gff_handle.close()

    logger.info("Starting to load %s", shelf_name)
    load_into_storage(shelf_name, exon_lines,
                      logger=logger, min_length=min_length, strip_cds=strip_cds, max_intron=max_intron)

    return new_ids


def load_from_gtf(shelf_name,
                  gff_handle,
                  label,
                  found_ids,
                  logger,
                  min_length=0,
                  max_intron=3*10**5,
                  is_reference=False,
                  strip_cds=False,
                  strand_specific=False):
    """
    Method to load the exon lines from GTF files.
    :param shelf_name: the name of the shelf DB to use.
    :param gff_handle: The handle for the GTF to be parsed.
    :param label: label to be attached to all transcripts.
    :type label: str
    :param found_ids: set of IDs already found in other files.
    :type found_ids: set
    :param logger: a logger to be used to pass messages
    :type logger: logging.Logger
    :param min_length: minimum length for a cDNA to be considered as valid
    :type min_length: int
    :param max_intron: maximum intron length for a cDNA to be considered as valid
    :type max_intron: int
    :param strip_cds: boolean flag. If true, all CDS lines will be ignored.
    :type strip_cds: bool
    :param strand_specific: whether the assembly is strand-specific or not.
    :type strand_specific: bool
    :param is_reference: boolean. If set to True, the transcript will always be retained.
    :type is_reference: bool
    :return:
    """

    exon_lines = dict()

    strip_cds = strip_cds and (not is_reference)
    strand_specific = strand_specific or is_reference

    # Reduce memory footprint
    [intern(_) for _ in ["chrom", "features", "strand", "attributes", "tid", "parent", "attributes"]]

    new_ids = set()
    to_ignore = set()
    for row in gff_handle:
        if row.is_transcript is True:
            if label != '':
                row.transcript = "{0}_{1}".format(label, row.transcript)
            if row.transcript in found_ids:
                __raise_redundant(row.transcript, gff_handle.name, label)
            if row.transcript in exon_lines:
                logger.warning(
                    "Multiple instance of %s found, skipping any subsequent entry", row.id)
                to_ignore.add(row.id)
                continue
                # __raise_invalid(row.transcript, gff_handle.name, label)
            if row.transcript not in exon_lines:
                exon_lines[row.transcript] = dict()
            if label:
                exon_lines[row.transcript]["source"] = label
            else:
                exon_lines[row.transcript]["source"] = row.source

            exon_lines[row.transcript]["features"] = dict()
            exon_lines[row.transcript]["chrom"] = row.chrom
            exon_lines[row.transcript]["strand"] = row.strand
            exon_lines[row.transcript]["attributes"] = row.attributes.copy()
            exon_lines[row.transcript]["tid"] = row.id
            exon_lines[row.transcript]["parent"] = "{}.gene".format(row.id)
            exon_lines[row.transcript]["strand_specific"] = strand_specific
            exon_lines[row.transcript]["is_reference"] = is_reference
            if "exon_number" in exon_lines[row.transcript]["attributes"]:
                del exon_lines[row.transcript]["attributes"]["exon_number"]
            continue

        if row.is_exon is False or (row.is_cds is True and strip_cds is True):
            continue
        if label != '':
            row.transcript = "{0}_{1}".format(label, row.transcript)
        if row.transcript in found_ids:
            __raise_redundant(row.transcript, gff_handle.name, label)
        assert row.transcript is not None
        if row.transcript not in exon_lines:
            exon_lines[row.transcript] = dict()
            if label:
                exon_lines[row.transcript]["source"] = label
            else:
                exon_lines[row.transcript]["source"] = row.source
            exon_lines[row.transcript]["features"] = dict()
            exon_lines[row.transcript]["chrom"] = row.chrom
            exon_lines[row.transcript]["strand"] = row.strand
            exon_lines[row.transcript]["exon"] = []
            exon_lines[row.transcript]["attributes"] = row.attributes.copy()
            exon_lines[row.transcript]["tid"] = row.transcript
            exon_lines[row.transcript]["parent"] = "{}.gene".format(row.transcript)
            exon_lines[row.transcript]["strand_specific"] = strand_specific
            exon_lines[row.transcript]["is_reference"] = is_reference
        else:
            if row.transcript in to_ignore:
                continue
            if "exon_number" in row.attributes:
                del row.attributes["exon_number"]
            if ("chrom" not in exon_lines[row.transcript] or
                    exon_lines[row.transcript]["chrom"] != row.chrom or
                    exon_lines[row.transcript]["strand"] != row.strand):
                __raise_invalid(row.transcript, gff_handle.name, label)
            exon_lines[row.transcript]["attributes"].update(row.attributes)
        if row.feature not in exon_lines[row.transcript]["features"]:
            exon_lines[row.transcript]["features"][row.feature] = []
        exon_lines[row.transcript]["features"][row.feature].append((row.start, row.end, row.phase))
        new_ids.add(row.transcript)
    gff_handle.close()
    logger.info("Starting to load %s", shelf_name)
    load_into_storage(shelf_name,
                      exon_lines,
                      logger=logger, min_length=min_length, strip_cds=strip_cds, max_intron=max_intron)

    return new_ids


def load_from_bed12(shelf_name,
                    gff_handle,
                    label,
                    found_ids,
                    logger,
                    min_length=0,
                    max_intron=3*10**5,
                    is_reference=False,
                    strip_cds=False,
                    strand_specific=False):
    """
    Method to load the exon lines from GTF files.
    :param shelf_name: the name of the shelf DB to use.
    :param gff_handle: The handle for the GTF to be parsed.
    :param label: label to be attached to all transcripts.
    :type label: str
    :param found_ids: set of IDs already found in other files.
    :type found_ids: set
    :param logger: a logger to be used to pass messages
    :type logger: logging.Logger
    :param min_length: minimum length for a cDNA to be considered as valid
    :type min_length: int
    :param max_intron: maximum intron length for a cDNA to be considered as valid
    :type max_intron: int
    :param strip_cds: boolean flag. If true, all CDS lines will be ignored.
    :type strip_cds: bool
    :param strand_specific: whether the assembly is strand-specific or not.
    :type strand_specific: bool
    :param is_reference: boolean. If set to True, the transcript will always be retained.
    :type is_reference: bool
    :return:
    """

    exon_lines = dict()

    strip_cds = strip_cds and (not is_reference)
    strand_specific = strand_specific or is_reference

    # Reduce memory footprint
    [intern(_) for _ in ["chrom", "features", "strand", "attributes", "tid", "parent", "attributes"]]

    new_ids = set()
    to_ignore = set()
    for row in gff_handle:
        # Each row is a transcript
        transcript = Transcript(row)
        if label != '':
            transcript.id = "{0}_{1}".format(label, transcript.id)
            if transcript.id in found_ids:
                __raise_redundant(transcript.id, gff_handle.name, label)
            if transcript.id in exon_lines:
                logger.warning(
                    "Multiple instance of %s found, skipping any subsequent entry", row.id)
                to_ignore.add(row.id)
                continue
            else:
                exon_lines[transcript.id] = dict()
            if label:
                exon_lines[transcript.id]["source"] = label
            else:
                exon_lines[transcript.id]["source"] = gff_handle.name  # BED12 files have no source
            exon_lines[transcript.id]["features"] = dict()
            exon_lines[transcript.id]["chrom"] = row.chrom
            exon_lines[transcript.id]["strand"] = row.strand
            exon_lines[transcript.id]["attributes"] = dict()  # BED12 files have no attributes
            exon_lines[transcript.id]["tid"] = transcript.id
            exon_lines[transcript.id]["parent"] = "{}.gene".format(transcript.id)
            exon_lines[transcript.id]["strand_specific"] = strand_specific
            exon_lines[transcript.id]["is_reference"] = is_reference
            exon_lines[transcript.id]["features"]["exon"] = [
                (exon[0], exon[1]) for exon in transcript.exons
            ]
            if transcript.is_coding and not strip_cds:
                exon_lines[transcript.id]["features"]['CDS'] = [
                    (exon[0], exon[1]) for exon in transcript.combined_cds
                ]
                exon_lines[transcript.id]["features"]["UTR"] = [
                    (exon[0], exon[1]) for exon in transcript.five_utr + transcript.three_utr
                ]
        new_ids.add(transcript.id)
    gff_handle.close()
    load_into_storage(shelf_name, exon_lines,
                      logger=logger, min_length=min_length, strip_cds=strip_cds, max_intron=max_intron)

    return new_ids