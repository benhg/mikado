from ..loci.reference_gene import Gene
import magic
from ..exceptions import CorruptIndex
from ..utilities.log_utils import create_null_logger
import sqlite3
import json
from time import sleep
import msgpack
import logging


class GeneDict:

    def __init__(self, dbname: str, logger=None, exclude_utr=False, check=True, protein_coding=False):

        self.__dbname = dbname
        self.__logger = create_null_logger()
        self.logger = logger
        if check is True:
            try:
                check_index(dbname, self.logger)
            except CorruptIndex:
                raise
        self.__exclude_utr = exclude_utr
        self.__protein_coding = protein_coding
        self.__db = sqlite3.connect("file:{}?mode=ro".format(self.__dbname), uri=True)
        self.__cursor = self.__db.cursor()
        self.__cache = dict()

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, logger):
        if logger is None:
            self.__logger = create_null_logger()
        elif not isinstance(logger, logging.Logger):
            raise TypeError("Invalid logger")
        else:
            self.__logger = logger

    @property
    def positions(self):
        return iter(self.__cursor.execute("SELECT chrom, start, end, gid FROM positions"))

    def get_position(self, chrom, start, end):
        for row in self.__cursor.execute(
                "SELECT gid FROM positions WHERE chrom=? AND start=? AND end=?", (chrom, start, end)):
            yield row[0]

    def __getitem__(self, item):

        if item in self.__cache:
            return self.__cache[item]

        failed = 0
        while True:
            try:
                res = self.__cursor.execute("SELECT json from genes where gid=?", (item,)).fetchmany()
                break
            except sqlite3.OperationalError as exc:
                failed += 1
                if failed > 10:
                    raise sqlite3.OperationalError(exc)
                sleep(3)

        if res:
            try:
                gene = self.__load_gene(res[0][0])
                self.__cache[item] = gene
                return gene
            except IndexError:
                raise IndexError(res)
        else:
            return None

    def __load_gene(self, jdict):
        gene = Gene(None, logger=self.logger)
        if not isinstance(jdict, dict):
            try:
                jdict = msgpack.loads(jdict, raw=False)
            except TypeError:
                jdict = json.loads(jdict)

        gene.load_dict(jdict, exclude_utr=self.__exclude_utr, protein_coding=self.__protein_coding)
        gene.finalize()
        return gene

    def load_all(self):

        for row in self.__cursor.execute("SELECT gid, json from genes"):
            gid, gene = row[0], self.__load_gene(row[1])
            self.__cache[gid] = gene
            # yield (gid, gene)

    def __iter__(self):
        self.__db.row_factory = lambda cursor, row: row[0]
        cursor = self.__db.cursor()
        for gid in cursor.execute("SELECT gid from genes"):
            yield gid
        self.__db.row_factory = None

    def items(self):

        for gid in self:
            yield (gid, self[gid])


def check_index(reference, queue_logger):
    wizard = magic.Magic(mime=True)

    if reference.endswith("midx"):
        reference = reference
    else:
        reference = "{}.midx".format(reference)

    if wizard.from_file(reference) == b"application/gzip":
        queue_logger.warning("Old index format detected. Starting to generate a new one.")
        raise CorruptIndex("Invalid index file")

    try:
        conn = sqlite3.connect(reference)
        cursor = conn.cursor()
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        if sorted(tables) != sorted([("positions",), ("genes",)]):
            raise CorruptIndex("Invalid database file")
        # res = cursor.execute("PRAGMA integrity_check;").fetchone()
        # if res[0] != "ok":
        #     raise CorruptIndex("Corrupt database, integrity value: {}".format(res[0]))
        gid, obj = cursor.execute("SELECT * from genes").fetchone()
        try:
            obj = msgpack.loads(obj, raw=False)
        except TypeError:
            try:
                obj = json.loads(obj)
            except (ValueError, TypeError, json.decoder.JSONDecodeError):
                raise CorruptIndex("Corrupt index")
            raise CorruptIndex("Old index, deleting and rebuilding")

        gene = Gene(None)
        try:
            gene.load_dict(obj)
        except:
            raise CorruptIndex("Invalid value for genes, indicating a corrupt index. Deleting and rebuilding.")

    except sqlite3.DatabaseError:
        raise CorruptIndex("Invalid database file")


