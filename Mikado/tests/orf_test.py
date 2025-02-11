# coding: utf-8

"""
Test for the BED12 module.
"""

import unittest
from Bio import Seq, SeqRecord
from ..parsers import bed12, GTF, GFF
from ..loci import Transcript
from re import sub


class OrfTester(unittest.TestCase):
    """
    Basic tests to verify that the BED12 library functions as intended.
    """

    def setUp(self):
        """
        Starting operations
        """

        seq1 = """CCGAAGAAGAACAAATTCCTTGCTGAATCATGGCGAAGTTGAAGCTCTACTCTTACTGGA
GAAGCTCATGTGCTCATCGCGTCCGTATCGCCCTCACTTTAAAAGGGCTTGATTATGAAT
ATATACCGGTTAATTTGCTCAAAGGGGATCAATCCGATTCAGATTTCAAGAAGATCAATC
CAATGGGCACTGTACCAGCGCTTGTTGATGGTGATGTTGTGATTAATGACTCTTTCGCAA
TAATAATGTACCTGGATGATAAGTATCCGGAGCCACCGCTGTTACCAAGTGACTACCATA
AACGGGCGGTAAATTACCAGGCGACGAGTATTGTCATGTCTGGTATACAGCCTCATCAAA
ATATGGCTCTTTTTGTGAGAAGATGAGATTAATAGGTATCTCGAGGACAAGATAAATGCT
GAGGAGAAAACTGCTTGGATTACTAATGCTATCACAAAAGGATTCACAGGTTTATAACGA
CCTGTCTGATAATGTCTCATATGTCCTTCAGCTCTCGAGAAACTGTTGGTGAGTTGCGCT
GGAAAATACGCGACTGGTGATGAAGTTTACTTGGCTGATCTTTTCCTAGCACCACAGATC
CACGCAGCATTCAACAGATTCCATATTAACATGGAACCATTCCCGACTCTTGCAAGGTTT
TACGAGTCATACAACGAACTGCCTGCATTTCAAAATGCAGTCCCGGAGAAGCAACCAGAT
ACTCCTTCCACCATCTGATTCTGTGAACCGTAAGCTTCTCTCAGTCTCAGCTCAATAAAA
TCTC"""
        self.seq1 = SeqRecord.SeqRecord(Seq.Seq(seq1.replace("\n", "")), id="CLASS_2.159")

        seq2 = """ACAAAACAAAGTAATCGCGAAAACACACAACAATCGCTGGACTCTGCTACTGCGAAGAAC
AACAAATTCCTTGTTTATCATGGCGAATTCCGGCGAAGAGAAGTTGAAGCTCTACTCTTA
CTGGAGAAGCTCGTGTGCTCATCGTGTCCGTATCGCCCTCGCTTTGAAAGGGCTTGATTA
TGAGTATATACCAGTGAATTTGCTCAAGGGTGATCAATTCGATTCAGTTTATCGTTTTGA
TCTTCAAGATTTCAAGAAGATCAATCCAATGGGAACTGTACCAGCTCTGGTGGATGGAGA
TGTTGTGATTAATGATTCTTTTGCGATAATAATGTATCTGGATGAGAAGTACCCTGAGCC
ACCTTTGTTACCTCGTGACCTCCATAAACGAGCTGTGAATTACCAGGCAATGAGTATTGT
CTTGTCTGGCATACAGCCTCATCAAAATCTGGCTGTTATTAGGTATATCGAGGAAAAGAT
AAATGTGGAGGAGAAGACTGCCTGGGTTAATAATGCTATCACAAAAGGATTTACAGCTCT
CGAGAAACTGTTGGTGAATTGCGCTGGGAAACATGCGACTGGTGATGAAATTTACCTGGC
TGATCTCTTTCTAGCACCACAGATCCACGGAGCAATCAACAGATTCCAGATTAACATGGA
ACCGTACCCAACTCTTGCAAAATGTTACGAATCATACAACGAACTGCCTGCGTTTCAAAA
TGCACTACCGGAAAAGCAGCCAGATGCTCCTTCTTCCACCATCTGATTCTGTGAACCCAT
AAGCTACTCTCACTTTAATAAAACCTCAG"""

        self.seq2 = SeqRecord.SeqRecord(Seq.Seq(seq2.replace("\n", "")), id="CLASS_2.160")

        seq3 = """GATGCCCTTAGTTTCTCTACTTGTATCATACAATAAAGGTCACAGATTTTGAAATTTGCAAAGATATATC
ATACATTCTCAGAGGAAGCCTTTGTCTCTAAGACTCTGGACCGTCTCCTTAACCGCATCTTCAACCGCAG
TAAAAACCAGCCCGAGCTCAATCAATCGCTTAGCCGCATCATTACACGACGTAAGCCCAGGTTGAGTCTC
TTTATCAAACTTGTGAACAGCAAACTCAGGGAAGAGCTTAGACACAAGAGCAGCAAACTCACTGAACTGA
TAAATCCCATTAGTGCATAAAAACCGTCCAGAAGCGTCAGGTGTTTCGAATAGCATCACATGACCTTTAG
CCACATCTTTCACGTGAACCACACCGAGCCAGTGATGCTCTTGCGTCTCGGTCGAGCCTTGTAAAAGCTG
TAGCAGAACAGCACAGCTTGCGTTTAGGTTCGGTTGCAGAAGCGGTCCGAGACATGTTGATGGATGAATC
GTCACAATGTTGGTTCCATGCTTCTCCGAAAATTCCCAAGCTGCTTTCTCAGCTAATGTCTTCGAAATTG
GATACCATTTCTAAAATCAAAATTATATACCAATCGTTACAAATATCATATAAATCATCACTAACCATTT
TAAACCGAAATTTAACGAACCTGCCTCGACTTGCAAAAATCAAGATCGGACCACGACGACTCATCGACGG
GAACTTTTTCCGGCCAATTAGGGTTAGGAACCAATGCGGAGATAGATGACGTGATCACCACGCGTCTCAC
ATTAAACCTCTTAGCAGCTTCCAACACATTGATCGTTCCCTTAACCGCCGGTTCGACCAGCTCCTTCTCT
GGATCTACCGGTGGATCCAACGTACAAGGTGACGCCACGTGGAACACTCCCGCACATCCATCAATAGCTC
TGGAGATTGCATCAGAGTCTAAGAGATCCGCTTCAAAGATCTTGATCTTAGAATCGGATCCGGGTAGTTG
CAGAAGATGAGTCGGGTCGGATCCTGGGTAAATCGAAGCGTGGATTTTAGTATATCCTTTCTCAATTAAC
GTTCGGATTATCCAAGATCCGATGAAACCATTAGCTCCGGTTACACACACTGTCTCTTTCGCCATTGTTG
ATCAATAAGCGCTCACTGAGAATTTTTTTGTTCTCTCTCTCTATCGCAATTTATCTCAGAAGATAAGAAA
AAAAAAACATCTTTCCAGTAAAAAAGGATCCTTTGTTTTTTTCTTACACGTAAAAAATGGATTTTTTTTT
CTCTCTTAAAGATATAATGCGTTGATACAAAAGCGTAACGTTGACATGATATTATCCACTAGTTTTATAG
ACTTTTCAAAAAAAGGAGAGAATTTTCAATTCTTCAGTAGTCAAATAGATGAAGACCGCCGGAGCGCCGC
CGCAGAGAGGTGGTTCCTCTTCCTCCTCCGCCGTATACTTTAACTGGTCTTCATCATCTTGTTCTTACGA
TAGCTGTAGAGTTTTGGTGGTGAAGATGGGAGGAAAAAGCAAGAAGCCTCATCAATCTTCTTCTTTTAAG
GAGTCAGAGCCAGAACCACCGAGAATCAAATCCAATGTTAAGCATAACTTGCAGCTTCTCAAGTTATGGA
AGGAGTTTCAGAGCAGAGGATCTGGCATGGCTAAGCCAGCGACTAGTTACAGGAAGAAGAAAGTAGAGAA
AGACGAGTTACCGGATGATAGCGAGCTCTACCGGGATCCTACAAATACGCTTTACTACACGAACCAAGGT
CTATTGGATGACGCAGTTCCGGTTTTGCTTGTTGATGGTTATAATGTGTGTGGATATTGGATGAAGTTAA
AGAAACATTTCATGAAAGGAAGGCTTGACGTTGCTCGGCAGAAGTTAGTTGATGAACTTGTGTCCTTCAG
TATGGTTAAAGAGGTTAAGGTAGTGGTTGTGTTTGATGCTCTCATGTCTGGTCTTCCTACTCACAAGGAA
GACTTTGCAGGTGTTGATGTGATTTTCTCAGGAGAAACTTGTGCTGACGCTTGGATTGAAAAGGAGGTGG
TTGCATTGAGAGAAGATGGATGCCCCAAGGTTTGGGTTGTAACATCTGATGTCTGTCAACAACAAGCAGC
ACATGGAGCGGTATTGGGGCATCATATCGATGTTATAAACTCGTTATGTTCATATCTTGTTTTTGATTTT
GGTGACTGATTCTTGACAGGGAGCTTATATTTGGAGTAGCAAGGCATTGGTTTCTGAGATTAAATCGATG
CATAAGGAGGTTGAGAAAATGATGCAAGAAACAAGGTCAACATCTTTCCAAGGGAGATTGCTTAAACACA
ATCTTGATTCTGAAGTCGTTGATGCTCTTAAAGATCTTAGAGACAAATTATCAGAAAACGAAACAAAGAG
ATGACAAAAAGACCAATCCGGATTATATAAACAATTAACAAGGCTTGGTCTCTCCATGTAACTTCTGTCC
CAAGTAAGTAAGCTAATCTGACTTGTAAAAAACAGAGGCTGCAGAGGAAACGAGGGAGATAGAGAGAGAG
AGAGCTCAAATGCTTTGTTATTGTTGTATTTGTGTCTGAATTCTTTTTGACTAATCTATATATAGATTCG
TTTTCTTTGGTCCAAACATATGGTTAAAAGATAGTTCTGAATTTTTCTTTTAGCTTCATGCATAAGAATC
ATCTTAACCTAATAACCTATGTTTATTATTTTACAATAATGTAAAAATGTAAATTTTTAGTTGAATAATG
AACCAAATTTTTATGTAAAAAAACTTGGATGTTTATTTTCAAACACAAACATCAGTAACACTTGAAGCAG
TAGAGAGAATTGGAGGCAGAGCAAGTCTACAAATTTGCAGATAGTTCCAGGGTTTGAGCTGTTTGTTCTG
GTCAGTCTCCAATCAATCAAAGCATATGGTTTATCGAGAATGGATAGAGATTCAAGAGAAGATTGAAGAA
CTGAGTTTGCAAAGGCTTATCAATGCCTTCGACTTCGAGTTGAGATTGAAGAAAAGGTAAAGAAATAGCA
AGTGATCTTTTGAAAATAGATCTCATATATTAATGACTTTCCATGTCTGTATTTGCTGAAGTTGATCTGA
ATTTGCATATTGTTCATGTCAATGGATTGTCTGCTGTTACTAAATTTAACTTTGTGTCAGCACTCTTTAC
GTTTTGAATTGTCGAACCATTCACTTGTTCAGTTATTATTTGGTCTATCCATCCTTATATGTTGTTCTCT
GTTTAGATAAGGACAAAGAATAGACACCAGAGGAACTGAACCAAACAGCTGAGGCAGTTGGATATGGTGC
GGTGAAGTAAGTATACGTATCATCTCTATTCTACTGGTCACATGTCATGAGCAGGGAAATTACAGCCGTT
TATCAGAAAGTCTGGCAAAGACATAGATGAGCTGAAACAGACGGTTGAGGAAGCTTACACCAACTTGTTA
CCGAGCGTACTGTGCGAGTACCTCTACAGATTATCTGAACACTACACGGACTAGCGTACCATGAAATTTG
TGGATTGGCCTCTGCAGCTTTGTTTGAAATTCACTATAGCTTAGATGGCGAATTGGATTTAGACATGGAC
TTCCGGATTGTATGTTGTCTTTGAGTCTCAAGGGATTGATTAATGTGATGATATTTATACACCATAGCTG
AAATGAAATTTGTACTTAAAACTGATGGATAATTAATAACAGA"""

        self.seq3 = SeqRecord.SeqRecord(Seq.Seq(seq3.replace("\n", "")), id="PRJEB7093_DN.7194.1")

        seq4 = """GATGCCCTTAGTTTCTCTACTTGTATCATACAATAAAGGTCACAGATTTTGAAATTTGCA
AAGATATATCATACATTCTCAGAGGAAGCCTTTGTCTCTAAGACTCTGGACCGTCTCCTT
AACCGCATCTTCAACCGCAGTAAAAACCAGCCCGAGCTCAATCAATCGCTTAGCCGCATC
ATTACACGACGTAAGCCCAGGTTGAGTCTCTTTATCAAACTTGTGAACAGCAAACTCAGG
GAAGAGCTTAGACACAAGAGCAGCAAACTCACTGAACTGATAAATCCCATTAGTGCATAA
AAACCGTCCAGAAGCGTCAGGTGTTTCGAATAGCATCACATGACCTTTAGCCACATCTTT
CACGTGAACCACACCGAGCCAGTGATGCTCTTGCGTCTCGGTCGAGCCTTGTAAAAGCTG
TAGCAGAACAGCACAGCTTGCGTTTAGGTTCGGTTGCAGAAGCGGTCCGAGACATGTTGA
TGGATGAATCGTCACAATGTTGGTTCCATGCTTCTCCGAAAATTCCCAAGCTGCTTTCTC
AGCTAATGTCTTCGAAATTGGATACCATTTCTAAAATCAAAATTATATACCAATCGTTAC
AAATATCATATAAATCATCACTAACCATTTTAAACCGAAATTTAACGAACCTGCCTCGAC
TTGCAAAAATCAAGATCGGACCACGACGACTCATCGACGGGAACTTTTTCCGGCCAATTA
GGGTTAGGAACCAATGCGGAGATAGATGACGTGATCACCACGCGTCTCACATTAAACCTC
TTAGCAGCTTCCAACACATTGATCGTTCCCTTAACCGCCGGTTCGACCAGCTCCTTCTCT
GGATCTACCGGTGGATCCAACGTACAAGGTGACGCCACGTGGAACACTCCCGCACATCCA
TCAATAGCTCTGGAGATTGCATCAGAGTCTAAGAGATCCGCTTCAAAGATCTTGATCTTA
GAATCGGATCCGGGTAGTTGCAGAAGATGAGTCGGGTCGGATCCTGGGTAAATCGAAGCG
TGGATTTTAGTATATCCTTTCTCAATTAACGTTCGGATTATCCAAGATCCGATGAAACCA
TTAGCTCCGGTTACACACACTGTCTCTTTCGCCATTGTTGATCAATAAGCGCTCACTGAG
AATTTTTTTGTTCTCTCTCTCTATCGCAATTTATCTCAGAAGATAAGAAAAAAAAAACAT
CTTTCCAGTAAAAAAGGATCCTTTGTTTTTTTCTTACACGTAAAAAATGGATTTTTTTTT
CTCTCTTAAAGATATAATGCGTTGATACAAAAGCGTAACGTTGACATGATATTATCCACT
AGTTTTATAGACTTTTCAAAAAAAGGAGAGAATTTTCAATTCTTCAGTAGTCAAATAGAT
GAAGACCGCCGGAGCGCCGCCGCAGAGAGGTGGTTCCTCTTCCTCCTCCGCCGTATACTT
TAACTGGTCTTCATCATCTTGTTCTTACGATAGCTGTAGAGTTTTGGTGGTGAAGATGGG
AGGAAAAAGCAAGAAGCCTCATCAATCTTCTTCTTTTAAGGAGTCAGAGCCAGAACCACC
GAGAATCAAATCCAATGTTAAGCATAACTTGCAGCTTCTCAAGTTATGGAAGGAGTTTCA
GAGCAGAGGATCTGGCATGGCTAAGCCAGCGACTAGTTACAGGAAGAAGAAAGTAGAGAA
AGACGAGTTACCGGATGATAGCGAGCTCTACCGGGATCCTACAAATACGCTTTACTACAC
GAACCAAGGTCTATTGGATGACGCAGTTCCGGTTTTGCTTGTTGATGGTTATAATGTGTG
TGGATATTGGATGAAGTTAAAGAAACATTTCATGAAAGGAAGGCTTGACGTTGCTCGGCA
GAAGTTAGTTGATGAACTTGTGTCCTTCAGTATGGTTAAAGAGGTTAAGGTAGTGGTTGT
GTTTGATGCTCTCATGTCTGGTCTTCCTACTCACAAGGAAGACTTTGCAGGTGTTGATGT
GATTTTCTCAGGAGAAACTTGTGCTGACGCTTGGATTGAAAAGGAGGTGGTTGCATTGAG
AGAAGATGGATGCCCCAAGGTTTGGGTTGTAACATCTGATGTCTGTCAACAACAAGCAGC
ACATGGAGCGGGAGCTTATATTTGGAGTAGCAAGGCATTGGTTTCTGAGATTAAATCGAT
GCATAAGGAGGTTGAGAAAATGATGCAAGAAACAAGGTCAACATCTTTCCAAGGGAGATT
GCTTAAACACAATCTTGATTCTGAAGTCGTTGATGCTCTTAAAGATCTTAGAGACAAATT
ATCAGAAAACGAAACAAAGAGATGACAAAAAGACCAATCCGGATTATATAAACAATTAAC
AAGGCTTGGTCTCTCCATGTAACTTCTGTCCCAAGTAAGTAAGCTAATCTGACTTGTAAA
AAACAGAGGCTGCAGAGGAAACGAGGGAGATAGAGAGAGAGAGAGCTCAAATGCTTTGTT
ATTGTTGTATTTGTGTCTGAATTCTTTTTGACTAATCTATATATAGATTCGTTTTCTTTG
GTCCAAACATATGGTTAAAAGATAGTTCTGAATTTTTCTTTTAGCTTCATGCATAAGAAT
CATCTTAACCTAATAACCTATGTTTATTATTTTACAATAATGTAAAAATGTAAATTTTTA
GTTGAATAATGAACCAAATTTTTATGTAAAAAAACTTGGATGTTTATTTTCAAACACAAA
CATCAGTAACACTTGAAGCAGTAGAGAGAATTGGAGGCAGAGCAAGTCTACAAATTTGCA
GATAGTTCCAGGGTTTGAGCTGTTTGTTCTGGTCAGTCTCCAATCAATCAAAGCATATGG
TTTATCGAGAATGGATAGAGATTCAAGAGAAGATTGAAGAACTGAGTTTGCAAAGGCTTA
TCAATGCCTTCGACTTCGAGTTGAGATTGAAGAAAAGGTAAAGAAATAGCAAGTGATCTT
TTGAAAATAGATCTCATATATTAATGACTTTCCATGTCTGTATTTGCTGAAGTTGATCTG
AATTTGCATATTGTTCATGTCAATGGATTGTCTGCTGTTACTAAATTTAACTTTGTGTCA
GCACTCTTTACGTTTTGAATTGTCGAACCATTCACTTGTTCAGTTATTATTTGGTCTATC
CATCCTTATATGTTGTTCTCTGTTTAGATAAGGACAAAGAATAGACACCAGAGGAACTGA
ACCAAACAGCTGAGGCAGTTGGATATGGTGCGGTGAAGTAAGTATACGTATCATCTCTAT
TCTACTGGTCACATGTCATGAGCAGGGAAATTACAGCCGTTTATCAGAAAGTCTGGCAAA
GACATAGATGAGCTGAAACAGACGGTTGAGGAAGCTTACACCAACTTGTTACCGAGCGTA
CTGTGCGAGTACCTCTACAGATTATCTGAACACTACACGGACTAGCGTACCATGAAATTT
GTGGATTGGCCTCTGCAGCTTTGTTTGAAATTCACTATAGCTTAGATGGCGAATTGGATT
TAGACATGGACTTCCGGATTGTATGTTGTCTTTGAGTCTCAAGGGATTGATTAATGTGAT
GATATTTATACACCATAGCTGAAATGAAATTTGTACTTAAAACTGATGGATAATTAATAA
CAGA"""

        self.seq4 = SeqRecord.SeqRecord(Seq.Seq(seq4.replace("\n", "")), id="PRJEB7093_DN.7194.2")

        self.index = dict()
        self.index[self.seq1.id] = self.seq1
        self.index[self.seq2.id] = self.seq2
        self.index[self.seq3.id] = self.seq3
        self.index[self.seq4.id] = self.seq4

        self.bed1 = "\t".join(
            """CLASS_2.159    0    784    ID=CLASS_2.159|m.24650  0    +    29    386    0    1    784    0""".split())
        self.bed2 = "\t".join(
            "CLASS_2.160    0    809    ID=CLASS_2.160|m.34763 0    +    1    766    0    1    809    0".split())
        self.bed3 = "\t".join(
            "PRJEB7093_DN.7194.1  0 3683 ID=PRJEB7093_DN.7194.1|m.16659 0  -  641    1115  0  1    3683    0".split())
        self.bed4 = "\t".join(
            "PRJEB7093_DN.7194.2  0  3604 ID=PRJEB7093_DN.7194.2|m.16657 0 - 641    1115  0    1    3604    0".split())

    def test_b1(self):
        b1 = bed12.BED12(self.bed1, transcriptomic=True)
        self.assertEqual(b1.start, 1)
        self.assertEqual(len(b1), 784)
        self.assertEqual(b1.thick_start, 30)
        self.assertEqual(b1.thick_end, 386)

    def test_b2(self):
        b2 = bed12.BED12(self.bed2, transcriptomic=True)
        self.assertEqual(b2.start, 1)
        self.assertEqual(len(b2), 809)
        self.assertEqual(b2.thick_start, 2)
        self.assertEqual(b2.thick_end, 766)

    def test_b3(self):
        b3 = bed12.BED12(self.bed3, transcriptomic=True)
        self.assertFalse(b3.invalid)
        self.assertEqual(b3.start, 1)
        self.assertEqual(len(b3), 3683)

    def test_b4(self):
        b4 = bed12.BED12(self.bed4, transcriptomic=True)
        self.assertFalse(b4.invalid)
        self.assertEqual(b4.start, 1)
        self.assertEqual(len(b4), 3604)
        self.assertEqual(b4.cds_len, 1115 - 641, (b4.cds_len, 1115 - 641))

    def test_b1_seq(self):
        b1 = bed12.BED12(self.bed1, transcriptomic=True, fasta_index=self.index, coding=True)
        self.assertIn(str(self.index[b1.chrom][386 + 3:386 + 6].seq), ("TAG", "TGA", "TAA"))
        self.assertFalse(b1.invalid, b1.invalid_reason)
        self.assertTrue(b1.transcriptomic)
        self.assertTrue(b1.coding)

        self.assertEqual(b1.start, 1)
        self.assertEqual(len(b1), 784)
        self.assertEqual("ATG", str(self.index[b1.chrom][b1.thick_start - 1:b1.thick_start + 2].seq),
                         str(self.index[b1.chrom][b1.thick_start - 1:b1.thick_start + 2].seq))

        self.assertTrue(b1.has_start_codon, b1.validity_checked)
        self.assertEqual("ATG", b1.start_codon, b1.start_codon)
        self.assertEqual(b1.thick_start, 30)
        self.assertEqual(b1.thick_end, 386)

        self.assertTrue(b1.has_stop_codon)

    def test_b2_seq(self):
        b2 = bed12.BED12(self.bed2,
                         transcriptomic=True,
                         fasta_index=self.index,
                         max_regression=0.3)
        self.assertNotIn(str(self.index[b2.chrom][766 + 3:766 + 6].seq), ("TAG", "TGA", "TAA"))
        self.assertEqual(b2.start, 1)
        self.assertEqual(len(b2), 809)
        self.assertTrue(b2.has_start_codon,
                        (b2.thick_start, b2.thick_end, self.bed2.split("\t")[6:8],
                        self.index[b2.chrom][b2.thick_start-1:b2.thick_end].seq.translate()))

    def test_b2_seq_no_start(self):
        b2 = bed12.BED12(self.bed2,
                         transcriptomic=True,
                         fasta_index=self.index,
                         max_regression=0)
        self.assertNotIn(str(self.index[b2.chrom][766 + 3:766 + 6].seq), ("TAG", "TGA", "TAA"))
        self.assertEqual(b2.start, 1)
        self.assertEqual(len(b2), 809)
        self.assertFalse(b2.has_start_codon,
                        (b2.thick_start, b2.thick_end, self.bed2.split("\t")[6:8],
                        self.index[b2.chrom][b2.thick_start + (3 - b2.phase - 1) % 3 - 1:
                                             b2.thick_end].seq.translate()))

    def test_b3_seq(self):
        b3 = bed12.BED12(self.bed3, transcriptomic=True, fasta_index=self.index)
        self.assertFalse(b3.invalid, (len(b3), len(self.index[b3.id]), b3.invalid_reason,
                                      (b3.thick_end, b3.thick_start), (b3.thick_end - b3.thick_start + 1) % 3))

    def test_b4_seq(self):
        b4 = bed12.BED12(self.bed4, transcriptomic=True, fasta_index=self.index)
        self.assertFalse(b4.invalid, (len(b4), b4.invalid_reason, len(self.index[b4.id])))
        self.assertTrue(b4.has_start_codon)
        self.assertTrue(b4.has_stop_codon)
        self.assertTrue(b4.thick_start, 641)
        self.assertTrue(b4.thick_end, 1112)
        self.assertTrue(b4.cds_len, 1112 - 641)


class OrfRelocatorTester(unittest.TestCase):

    def setUp(self):

        self.bed_row = "\t".join("TRIAE_CS42_1AL_TGACv1_000002_AA0000030.1	0	3539	TRIAE_CS42_1AL_TGACv1_000002_AA0000030.1|m.13	0	+	2	2969	0	1	3539	0".split())
        self.sequence = """ATCGAGCAGATTGGCCGCAACCTACAACTCCCACGGCCCAAGCACTCTCTCTCTCTCTTTCCCTCTCACC
CTCGCCTCCGCTCCCCCATTTCCGAAGTACTCGCGAGCCAGCGGCCTCCAGCTCACCACCGTTTCCGCCG
CGCGCAGATCCGCCCAATCCGTGCAGCCTCAGGCCACCGCTCTGGTTCCGTGACATGTGGCGAGGTGGTG
GCGCAGACGCTGATGCAGGAGGCGCTCGCGAGGCTGAGGAGCACAACAATGTCGAGGAAGAGGAAGGGAG
TGAGGATGGAGATCGGGACCTGCAGAATAAACGTCCTAAAGTGGGTGCTTTTGGCGAAGAAAGCTCTGGT
GTTAATGCATCCTTCTTTGGATATGAAGCACCACATTTGCATGCTTTTGCTGAACATGACCATTTGAAGC
TGTCACATGGTCCAGAAAATGAATTGGATTTTGGTTTGTCGCTTATCTCAAATGATGGTGGGAATGATAT
TCCAAGGGAGACCAACAGTCATGGTGTCTGTGATGTAGAAAGATCAGGTGGAACAAATGCAGAAGATCTT
GAAATAAGAATGGACCTATCTGATGATCTCTTGCACCTGATATTCTCCTTCTTATGCCAGAAGGATTTAT
GTAGAGCAGGGGCTGCCTGCAAACAGTGGCAGTCTGCTAGTATGCATGAGGATTTCTGGAAATATTTGAA
GTTTGAGAACACCAGAATATCTCTGCAGAACTTTGTTAATATTTGCCACCGTTATCAGAATGTGACAAAT
CTCAATTTGTCTGGTGTCTTAAGTGCAGAAAGCCTAGTGATTGAAGCAATAACATTCTTAAGGCATCTTA
AGACCTTGATAATGGGCAAGGGACAACTGGGAGAAACATTTTTTCAGGCTTTGGCTGAATGCCCATTGTT
AAATACTTTAACAGTCAGTGATGCATCCCTTGGTAGTGGCATTCAAGAGGTAACTGTTAATCATGATGGA
TTGCATGAACTTCAAATTGTGAAGTGTCGTGCACTCAGAGTATCTATCAGATGCCACCAACTTCGAATAC
TGTCTCTGAGGAGAACTGGCATGGCTCATGTATCACTCAATTGTCCTCAGTTGCTTGAATTGGATTTTCA
GTCCTGCCATAAGCTTTCTGACACTGCAATTCGTCAAGCAGCGACAGCCTGTCCACTGTTAGCGTCACTA
GATATGTCATCCTGCTCGTGTGTTACTGATGAGACATTGCGTGAGATAGCTAATGCATGTCAAAATCTTT
CTGTTCTTGATGCATCTAACTGCCCCAACATTTCTTTCGAGTCGGTAAAGCTTCCAATGTTGGTAGACTT
GAGACTATCAAGTTGTGAGGGAATCACATCTGCTTCAATGGGTGCAGTATGTTTTAGTCGTATACTTGAG
GCGTTGCAACTTGATAATTGTAGCCTGTTGACATCTGTGTCTTTGGATCTGCCACATCTCAAGAATATTA
GTCTTGTACACCTCCGCAAGTTTGCTGATTTAAATCTGCGAAGCCCTGTGCTTTCTTACATAAAAGTTTC
CAGATGCTCAGCACTTCGTTGTGTTACCATAACATCAAATGCTCTTAAGAAACTGGTGCTTCAAAAACAA
GAGAGCCTATGTAATTTATCATTGCAATGCCACAATTTAATTGATGTTGATCTTAGTGATTGCGAGTCAT
TGACAAATGAGATCTGCAAAGTTCTCAGTGACGGAGGGGGTTGCCCCATGCTCAGGTCATTAATTCTTGA
TAATTGTGAGAGTTTGAGTGTCGTGGAACTGAATAATAGTTCTTTGGTTAATCTCTCACTTGCTGGTTGC
CGTTCCATGACATTCCTGAAACTTGCATGCCCAAAGCTTCAAGTGGTGATTCTTGATGGTTGTGATCATC
TTGAAAGAGCATCATTTTGCCCGGTTGGTCTTGAATCCCTAAACCTTGGAATTTGTCCAAAGTTGAGTGT
TCTACGCATAGAGGCCCCAAATATGTCTATATTGGAGCTGAAGGGCTGTGGTGTCCTTTCTGAGGCTTCA
ATTAATTGTCCTTGCTTGATATCTTTAGATGCCTCTTTCTGCAGACAGTTTATGGATGATTCGCTGTCCC
AAACAGCAGAAGCATGCCCTCTTATTGAACATCTTATATTGTCTTCATGTTTATCCATTGACGTCCGTGG
ATTGTCTTCTCTGCATTGCCTTCAGAAGCTGGCCTTGCTTGACCTATCATATACATTTTTGATGAACTTG
AAGCCGGTTTTTGACAGTTGTCTGCAGTTGAAGGTCTTGAAACTTTCAGCTTGCAAGTATCTCAGTGATT
CATCTTTGGAACCACTCTACAGAGAGGGTGCTCTACCGATGCTCGTTGAGCTAGATCTGTCCTACTCGTC
CATTGGGCAGACTGCAATAGAAGAGCTTCTCGCGTGCTGTACAAATTTGGTTAATGTGAACCTAAACGGA
TGTACGAACTTGCATGAATTGGTATGTGGATCAGACTATTGCCGGTCCGGTGACATGCCAATTGATGCTT
TCCCCCCTGATTCTGCACCAGACAAGACCAAAGAGATCAGGGAGAGTTCGGATTGTCAGCTTGAAGTTCT
CAGTTGTACTGGCTGTCCAAATATTAAGAAAGTTGTTATTCCTTCAACGGCCAACTATCTGAATTTGTCT
AAGATCAACCTTAATTTGTCTGCAAACTTGAAGGAAGTAGATTTGAAGTGCTCCAATCTTTACAATTTAA
ATTTGAGCAATTGTAACTCACTGGAGATTCTGAAGCTTGATTGCCCAAGATTGGCTAACCTCCAACTTTT
GGCATGCACAATGTTGCAAGAGGATGAACTGAAATCTGCACTATCCTTTTGCGGTGCATTGGAGATCCTC
AATGTGCACTCTTGTCCACAAATAAACACGCTGGATTTTGGCAGGCTACAGGCTGTTTGCCCAACTCTTA
AGCGCATCCAGAGCAGCCCCATCGCATAGTATGAAGGATTCTGGTCTTCTTAATGGACTCGAGTAAATAG
TCCAGATTTGAAACAGAAAAGGCCATGTCGTACTCTTGTACATATGCAGCACCGCCAATATATTGTATGG
CTGCATGTATTAGGGAGCCAGGGCTGACATGAAACCTGTTCTTCCAATCGATTTCTTGTGTTGAATCTAG
TTGAAACATGGAAACCGCACTTCCTAGTTTGTATTTGCTTTTGAGGTGCAGTGATGGAGTAAGCAGATCT
GTATTTATATGAATGAATAACCATCTTGTTTGGATCGTCGATGTTGTATGCTTCATTGATGACATGGGGT
GCTAAGTTTGACTGAAATTACACCAGGTTCTATGGTTCTCTCATAAGGTGCAGTGATTCTGCGGTCTTTA
TTAATCTGTCTCAACTGTGACGATGCAACTGAGACGTTTCCATCTGCCGGCTGCTGATGCTGTGAACTCT
TGGTAAAAAACCTGGTGTACTTGATCCAAGAGCATTCGTTGGGTCACTTGTATCCTTGAAAATTGAGTAA
CTAATAAATGCTGTTGTGTAAAAAAAAGGGGCTTTCTTT"""

        self.seq = SeqRecord.SeqRecord(Seq.Seq(self.sequence.replace("\n", "")),
                                       id="TRIAE_CS42_1AL_TGACv1_000002_AA0000030.1")

        self.index = dict()
        self.index["TRIAE_CS42_1AL_TGACv1_000002_AA0000030.1"] = self.seq

    def test_relocation(self):

        bed = bed12.BED12(self.bed_row, fasta_index=self.index,
                          transcriptomic=True,
                          max_regression=0.3)

        self.assertEqual(bed.thick_start, 195)
        self.assertEqual(bed.phase, 0)


class TestPartial(unittest.TestCase):

    def test_3_partial(self):

        line = "\t".join(
            ['class_Chr1.1004.0',
             '0',
             '1060',
             'ID=class_Chr1.1004.0|m.22214;class_Chr1.1004.0|g.22214;ORF_class_Chr1.1004.0|g.22214_class_Chr1.1004.0|m.22214_type:3prime_partial_len:300_(+)',
             '0',
             '+',
             '162',
             '1060',
             '0',
             '1',
             '1060',
             '0'])
        bed_line = bed12.BED12(line, transcriptomic=True)
        self.assertFalse(bed_line.invalid, bed_line.invalid_reason)

    def test_internal(self):

        sequence = """TCCTCACAGTTACTATAAGCTCGTCTATGGCCAGAGACGGTGGTGTTTCTTGTTTACGAA
GGTCGGAGATGATGAGCGTCGGTGGTATCGGAGGAATTGAATCTGCGCCGTTGGATTTAG
ATGAAGTTCATGTCTTAGCCGTTGATGACAGTCTCGTTGATCGTATTGTCATCGAGAGAT
TGCTTCGTATTACTTCCTGCAAAGTTACGGCGGTAGATAGTGGATGGCGTGCTCTGGAAT
TTCTAGGGTTAGATAATGAGAAAGCTTCTGCTGAATTCGATAGATTGAAAGTTGATTTGA
TCATCACTGATTACTGTATGCCTGGAATGACTGGTTATGAGCTTCTCAAGAAGATTAAGG
AATCGTCCAATTTCAGAGAAGTTCCGGTTGTAATCATGTCGTCGGAGAATGTATTGACCA
GAATCGACAGATGCCTTGAGGAAGGTGCTCAAGATTTCTTATTGAAACCGGTGAAACTCG
CCGACGTGAAACGTCTGAGAAGTCATTTAACTAAAGACGTTAAACTTTCCAACGGAAACA
AACGGAAGCTTCCGGAAGATTCTAGTTCCGTTAACTCTTCGCTTCCTCCACCGTCACCTC
CGTTGACTATCTCGCCTGA"""
        sequence = sub("\n", "", sequence)

        record = SeqRecord.SeqRecord(Seq.Seq(sequence), id="class_Chr1.1006.0")
        index = {record.id: record}

        line = "\t".join(
            ['class_Chr1.1006.0',
             '0',
             '619',
             'ID=class_Chr1.1006.0|m.22308;class_Chr1.1006.0|g.22308;ORF_class_Chr1.1006.0|g.22308_class_Chr1.1006.0|m.22308_type:internal_len:206_(+)',
             '0',
             '+',
             '2',
             '617',
             '0',
             '1',
             '619',
             '0'])

        bed_line = bed12.BED12(line, transcriptomic=True, fasta_index=index)
        self.assertFalse(bed_line.invalid, bed_line.invalid_reason)
        pep = sequence[bed_line.thick_start - 1 + 2:bed_line.thick_end]
        if len(pep) % 3 != 0:
            pep = pep[:-(len(pep) % 3)]
        pep = str(Seq.Seq(pep).translate())
        self.assertEqual(bed_line.phase, 2, (bed_line.thick_start, bed_line.thick_end, pep))
        self.assertFalse(bed_line.has_start_codon)
        self.assertFalse(bed_line.has_stop_codon)

        lines = """Chr1	CLASS	transcript	3442811	3443785	1000	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0"; exon_number "1"; Abundance "22.601495"; canonical_proportion "1.0";
    Chr1	CLASS	exon	3442811	3442999	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";
    Chr1	CLASS	exon	3443099	3443169	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";
    Chr1	CLASS	exon	3443252	3443329	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";
    Chr1	CLASS	exon	3443417	3443493	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";
    Chr1	CLASS	exon	3443582	3443785	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";"""

        lines = [GTF.GtfLine(_) for _ in lines.split("\n") if _]

        transcript = Transcript(lines[0])
        transcript.add_exons(lines[1:])
        transcript.finalize()
        transcript.load_orfs([bed_line])
        self.assertTrue(transcript.is_coding)
        self.assertFalse(transcript.has_start_codon)
        self.assertFalse(transcript.has_stop_codon)
        self.assertEqual(transcript.selected_cds_end, transcript.start)
        self.assertEqual(transcript.selected_cds_start, transcript.end)

    def test_regression(self):

        sequence = """TC
CTCACAGTTACTATAAGCTCGTCT
ATGGCCAGAGACGGTGGTGTTTCTTGTTTACGAA
GGTCGGAGATGATGAGCGTCGGTGGTATCGGAGGAATTGAATCTGCGCCGTTGGATTTAG
ATGAAGTTCATGTCTTAGCCGTTGATGACAGTCTCGTTGATCGTATTGTCATCGAGAGAT
TGCTTCGTATTACTTCCTGCAAAGTTACGGCGGTAGATAGTGGATGGCGTGCTCTGGAAT
TTCTAGGGTTAGATAATGAGAAAGCTTCTGCTGAATTCGATAGATTGAAAGTTGATTTGA
TCATCACTGATTACTGTATGCCTGGAATGACTGGTTATGAGCTTCTCAAGAAGATTAAGG
AATCGTCCAATTTCAGAGAAGTTCCGGTTGTAATCATGTCGTCGGAGAATGTATTGACCA
GAATCGACAGATGCCTTGAGGAAGGTGCTCAAGATTTCTTATTGAAACCGGTGAAACTCG
CCGACGTGAAACGTCTGAGAAGTCATTTAACTAAAGACGTTAAACTTTCCAACGGAAACA
AACGGAAGCTTCCGGAAGATTCTAGTTCCGTTAACTCTTCGCTTCCTCCACCGTCACCTC
CGTTGACTATCTCGCCTGA"""

        record = SeqRecord.SeqRecord(Seq.Seq(sub("\n", "", sequence)), id="class_Chr1.1006.0")
        index = {record.id: record}

        line = "\t".join(
            ['class_Chr1.1006.0',
             '0',
             '619',
             'ID=class_Chr1.1006.0|m.22308;class_Chr1.1006.0|g.22308;ORF_class_Chr1.1006.0|g.22308_class_Chr1.1006.0|m.22308_type:internal_len:206_(+)',
             '0',
             '+',
             '2',
             '617',
             '0',
             '1',
             '619',
             '0'])

        # Now we are going back to find the start codon
        bed_line = bed12.BED12(line, transcriptomic=True, fasta_index=index, max_regression=0.2)
        self.assertFalse(bed_line.invalid, bed_line.invalid_reason)
        self.assertEqual(bed_line.phase, 0)
        # Start codon in frame found at location 27
        self.assertEqual(bed_line.thick_start, 27)
        self.assertTrue(bed_line.has_start_codon)
        self.assertFalse(bed_line.has_stop_codon)

        lines = """Chr1	CLASS	transcript	3442811	3443785	1000	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0"; exon_number "1"; Abundance "22.601495"; canonical_proportion "1.0";
Chr1	CLASS	exon	3442811	3442999	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";
Chr1	CLASS	exon	3443099	3443169	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";
Chr1	CLASS	exon	3443252	3443329	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";
Chr1	CLASS	exon	3443417	3443493	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";
Chr1	CLASS	exon	3443582	3443785	.	-	.	gene_id "Chr1.1006.gene"; transcript_id "class_Chr1.1006.0";"""

        lines = [GTF.GtfLine(_) for _ in lines.split("\n") if _]

        transcript = Transcript(lines[0])
        transcript.add_exons(lines[1:])
        transcript.finalize()
        transcript.load_orfs([bed_line])
        self.assertTrue(transcript.is_coding)
        self.assertTrue(transcript.has_start_codon)
        self.assertFalse(transcript.has_stop_codon)
        self.assertEqual(transcript.selected_cds_end, transcript.start)
        self.assertEqual(transcript.selected_cds_start, transcript.end - 26)

    def test_partial_gff(self):
        line = 'All-stringtie-1-hisat2-0_Stringtie_hisat2-All-0.sorted.1.1\tProdigal_v2.6.3\tCDS\t2\t100\t1.4\t+\t0\tID=1_1;partial=10;start_type=Edge;rbs_motif=None;rbs_spacer=None;gc_cont=0.455;conf=58.12;score=1.43;cscore=-1.29;sscore=2.72;rscore=0.00;uscore=0.00;tscore=3.22;\n'
        sequence = "ACGATACAGAGTGATGGGGAACCCTCATAAAATGTTGATCTCAAGATACCCGGATCACGCACACAACTACGCGATCGACAG"\
        "AGAATACATAAGGAACTGAGAACACCGCCACACTACACCCTACAACACCTACACTCTCACAATAACGTGTACATCCTCTCTGGAGTTGAAAA"\
                "TTGAAGAGTGCTCCAGGGAGCTATCCTAACATAGGAACAGAGGTTGCTGGTACGTACGAAATAAGCAGTGCCTAGATGGAGTTCC"\
                "GAGTGCTTATTATTATTATTACTATTTGCTAGTACTCAGATTTACTGCAATATTGACCATTAGATGGCGTGACATCGGCTAACAA"\
                "AGTGTGCAGCATGAAACCCAGATAACATCTGAATACAACATTTTGGACTACAGACTACAACATTAGCCATTGCATTCATTCAACG"\
                "GTGTAATGCTAATCAAGTAAAAAAAAACTTGAATCAGGCAACTCATTTTCCATTTGATCAACGGAACAACAGTTCACAGCCAAAC"\
                "ATAGAGTGCGTGTGTGTAGAAAATGAAGAGCAGAAACCCACTGGTGTAAAGGATAAGTGCAGCTTGAGCTTTGTGTTTCAAACTT"\
                "GTATATTCCAGCAGTTAGCTGACCTTTGGAACAACTTGTGGCTGTAAATCTGGCTAAATCACTGGCTGTTTGCATCTTTAGCCGG"\
                "GAGAAATACCTGTACACTACTACCTTAAAATGGAAACCCAGAGTTGGTTCAATCCCATTGAGAAAATTAATATGCTGAACGTTTG"\
                "AGAGAGTAGTGAATGAAGAGAGCAACTGTAAAGCCAGGTTTCCTAACTGAACCTGACAGAGCAACAGGGACAGACAGTGTCTTCT"\
                "GACTGAGAGACGTCGTACACAATGAAATTTCCGGCAAAAAAGGAAAATCGTACAAACAAGATACTTACTACTGTAGAAGGAAAGA"\
                "AAGATATGGGTGAGAAATTGGTAGAGTGCTGCAACACCTGCGGATGGGGTCGTCGTAGTGGATCGCTGCTTGCCTGAGCATGCCG"\
                "ACGCCGTGACGCGCCCCCCGCGTCATCTCCTCCATGAATTCGGCGTCGATGAGGCGGACTTGAGGAACTGCTTCGAGGTAGTGGA"\
                "TTTGTGGGTACCGGAAGTACCCGTCGGCGCCGTCGTGGGGCGCCCTGCGACAGAGGAGGATTGGACGGGTGGTCTCTTCCTCTTC"\
                   "GAAGAAGCCGCGGGCGGCTGCCGCGGCGACTGCGACACCGTCCGCGTCCACCAAGGTGTGGGTGCGGGGCGGCTGCTGCTCCG"\
                   "GCAGGCGGAGGCCGTCTCCACCGCCCGCGAACCCCTCCAGAGGCAGAGGCAGAGGCAGAAGCAGGAGGTTCCTCCAGAGCCAC"\
                   "CAGACGACGACGACGGCCACAGGCGCGGCGAGGTGGAGGGCGAGGTAGGCCGCCGCAGAGGCGCACAAAGGGCGCGGCGGCGG"\
                   "GGCCGAGACGCAATCGAGATTCGGAATGCAAGACAGATTGGCGTACACAAGCTCAGGCATGGCCGCCGGCGACGCTGCTGGGG"\
                   "GTCGGAGAAGTTCCGGGGAAAGGGGAACGAACGAGGGCAGAAGCCTTTGGCCGTTTTTGCAAAGGTGTTGGTGGGTACTCTTTA"
        line = GFF.GffLine(line)
        b = bed12.BED12(line, transcriptomic=True, start_adjustment=True, lenient=False, sequence=sequence)
        assert b.thick_start == 1
        assert b.coding, b.phase
        assert not b.invalid, b.invalid_reason
        assert b.phase == 1, b.phase


if __name__ == '__main__':
    unittest.main()
