#!/usr/bin/env python3
import pandas as pd
import numpy as np
import itertools
import argparse


def get_overrides_transcript(overrides_tables, ensembl_table, hgnc_symbol, hgnc_canonical_genes):
    """Find canonical transcript id for given hugo symbol. Overrides_tables is
    a list of different override tables"""
    for overrides in overrides_tables:
        try:
            # corner case when there are multiple overrides for a given gene symbol
            if overrides.loc[hgnc_symbol].ndim > 1:
                transcript = overrides.loc[hgnc_symbol].isoform_override.values[0]
            else:
                transcript = overrides.loc[hgnc_symbol].isoform_override
            return transcript
        except KeyError:
            pass
    else:
        # get ensembl canonical version otherwise
        return get_ensembl_canonical_transcript_id_from_hgnc_then_ensembl(ensembl_table, hgnc_symbol, hgnc_canonical_genes, 'transcript_stable_id')


def pick_canonical_longest_transcript_from_ensembl_table(ensembl_rows, field):
    """Get canonical transcript id with largest protein length or if there is
    no such thing, pick biggest gene id"""
    return ensembl_rows.sort_values('is_canonical protein_length gene_stable_id'.split(), ascending=False)[field].values[0]


def get_ensembl_canonical(ensembl_rows, field):
    if (ensembl_rows.ndim == 1 and len(ensembl_rows) == 0) or (ensembl_rows.ndim == 2 and len(ensembl_rows) == 0):
        return np.nan
    elif ensembl_rows.ndim == 1:
        return ensembl_rows[field]
    elif ensembl_rows.ndim == 2:
        if len(ensembl_rows) == 1:
            return ensembl_rows[field].values[0]
        else:
            return pick_canonical_longest_transcript_from_ensembl_table(ensembl_rows, field)


def get_ensembl_canonical_transcript_id_from_hgnc_then_ensembl(ensembl_table, hgnc_symbol, hgnc_canonical_genes, field):
    """Determine canonical transcript based on hgnc mappings to ensembl id.
    If not possible use ensembl's data."""
    try:
        hgnc_gene_rows = hgnc_canonical_genes.loc[hgnc_symbol]
    except KeyError:
        raise(Exception("Unknown hugo symbol"))

    if hgnc_gene_rows.ndim == 1:
        result = get_ensembl_canonical(ensembl_table[ensembl_table.gene_stable_id == hgnc_gene_rows.ensembl_gene_id], field)
        if pd.isnull(result):
            # use ensembl data to find canonical transcript if nan is found
            # there's actually 222 of these (see notebook)
            try:
                return get_ensembl_canonical(ensembl_table.loc[hgnc_symbol], field)
            except KeyError:
                return np.nan
        else:
            return result
    else:
        raise(Exception("One hugo symbol expected in hgnc_canonical_genes"))


def lowercase_set(x):
    return set({i.lower() for i in x})


def ignore_rna_gene(x):
    return set({i for i in x if not i.startswith('rn') and not i.startswith('mir') and not i.startswith('linc')})


def ignore_certain_genes(x):
    ignore_genes = \
        {'trpc6p8', 'mocs2-dt', 'rmrpp3', 'en2-dt', 'zbtb47-as1', 'ufd1-as1', 'garin1a', 'ube2q2p13', 'ino80d-as1', 'tnpo1-dt', 'linc03028', 'linc02948', 'stat4-as1', 'hnrnpa1l3', 'atp8b1-as1', 'linc03006', 'lncatv', 'fam231b', 'ticam2-as1', 'stag2-as1', 'pramef3', 'erich2-dt', 'pik3ca-dt', 'glis3-as2', 'piwil2-dt', 'gpc1-as1', 'linc02985', 'fam88e', 'ptprt-dt', 'srsf8bp', 'eva1cp6', 'prpf39-dt', 'mphosph10p5', 'ier5l-as1', 'linc02984', 'sphar', 'tent5c-dt', 'gtf2i-as1', 'rfx3-dt', 'rnpc3-dt', 'pou2f2-as1', 'linc02945', 'linc03025', 'b4gat1-dt', 'pdk1-as1', 'eola2-dt', 'pcdhb1-as1', 'rnf32-dt', 'linc02970', 'lipt2-as1', 'pkd2l2-dt', 'linc02953', 'cfap276', 'gapdh-dt', 'tmem183bp', 'prim2bp', 'h2al3', 'cdk5r2-as1', 'rrbp1p2', 'linc02975', 'rab17-dt', 'linc02928', 'slc41a3-as1', 'eef1a1-as1', 'linc02941', 'chek2p6', 'icam4-as1', 'frmd3-as1', 'got1-dt', 'prkd3-dt', 'prdm8-as1', 'cdc20-dt', 'tmem132e-dt', 'pank1-as1', 'phb1p7', 'hnrnpk-as1', 'celsr1p1', 'hey2-as1', 's1pr1-dt', 'trpc6p5', 'prdm6-as1', 'gatd3', 'linc02974', 'h2al1q', 'linc02981', 'gatd1-dt', 'linc01610', 'rab4a-as1', 'zfhx3-as1', 'pls1p1', 'zc3h12a-dt', 'linc02940', 'garin1b', 'linc02973', 'rragc-dt', 'nfib-as1', 'klc2-as2', 'mrm3p2', 'mir219a2hg', 'xndc1n', 'jtb-dt', 'mir130ahg', 'mphosph10p6', 'hrg-as1', 'fars2-as1', 'btg1-dt', 'linc02936', 'tmlhep1', 'msrb3-as1', 'krbox5p1', 'prmt5-dt', 'znf225-as1', 'col6a2-dt', 'zbtb7c-as1', 'slc38a4-as1', 'hpvc1', 'tspan14-as1', 'linc02920', 'piwil4-as1', 'nrip3-dt', 'dbx2-as1', 'dcaf8-dt', 'calcrl-as1', 'stk4-dt', 'ubr5-dt', 'pknox2-dt', 'bicd1-as1', 'linc02914', 'trim8-dt', 'pcmtd1-dt', 'penk-as1', 'rpl7ap75', 'terlr1', 'ngfr-as1', 'pfn2-as1', 'xkr4-as1', 'linc02951', 'h2bc12l', 'arnt2-dt', 'nipal4-dt', 'linc03011', 'linc02926', 'camk2g-as1', 'sv2c-as1', 'enpp7p15', 'nup133-dt', 'krt10-as1', 'linc02949', 'phb1p15', 'dhx9-as1', 'chka-dt', 'mvp-dt', 'ccn2-as1', 'fam231d', 'lncrna-iur', 'linc02986', 'rbm12b-dt', 'linc02944', 'phb1p20', 'dsp-as1', 'slc17a6-dt', 'linc02960', 'trmt61a-dt', 'dmxl1-dt', 'tpt1p15', 'c4orf46p2', 'kcnc4-dt', 'rc3h1-dt', 'trpc6p6', 'fam231c', 'fam131b-as2', 'mphosph10p4', 'trim51g', 'pms2p14', 'crma', 'pdk4-as1', 'tacr3-as1', 'snd1-dt', 'lrrc58-dt', 'rpl6p11', 'nectin1-dt', 'rmrpp1', 'linc02995', 'borcs8p1', 'suclg2-dt', 'linc03000', 'linc02952', 'lrig3-dt', 'atf6-dt', 'fam231a', 'fam136fp', 'linc02913', 'linc03031', 'oxr1-as1', 'linc03024', 'rpl26l1-as1', 'balr6', 'arhgap11b-dt', 'rassf3-dt', 'zbed10p', 'znf778-dt', 'pinx1-dt', 'mir34bhg', 'csrp1-as1', 'rph3al-as2', 'kbtbd11-as1', 'myoz3-as1', 'khdc1-as1', 'kcnq5-dt', 'linc02930', 'ube2e2-dt', 'retreg1-as1', 'znf888-as1', 'mphosph10p2', 'tiam1-as1', 'tdrd6-as1', 'upk3bl3p', 'lto1p1', 'linc03020', 'linc02916', 'rusf1-dt', 'snx30-dt', 'prkag2-as2', 'phb1p10', 'chuk-dt', 'cops8-dt', 'phb1p18', 'linc03021', 'pydc2-as1', 'ypel3-dt', 'wdr11-dt', 'pard3-dt', 'rpap3-dt', 'pelp1-dt', 'pierce2', 'pdcd6p1', 'c2cd5-as1', 'akap2', 'dnpep-as1', 'porcn-dt', 'phb1p6', 'usp38-dt', 'cenpbd1p', 'rpl7ap74', 'cstpp1', 'adam7-as1', 'xndc1n-znf705ep-alg1l9p', 'jakmip3-as1', 'gsk3b-dt', 'ldaf1', 'cmklr2', 'gad3p', 'ercc6l2-as1', 'linc02982', 'cldn14-as1', 'scmh1-dt', 'ankrd17-dt', 'linc02967', 'poglut2p1', 'linc02942', 'znf496-dt', 'flvcr2-as1', 'sanbr', 'tmem217b', 'linc03022', 'spns2-as1', 'linc03016', 'rpl7ap77', 'iqsec3-as1', 'cfap141', 'mir365bhg', 'lhx2-as1', 'sgsm2-as1', 'linc02931', 'deptor-as1', 'cspg4p8', 'rnase2cp', 'aqp5-as1', 'npcdr1', 'fcgr1bp', 'btbd3-as1', 'znf584-dt', 'linc02943', 'tmem44-as2', 'prkch-as1', 'ciao2ap2', 'skap1-as2', 'mir493hg', 'fndc1-as1', 'rack1p3', 'phb1p4', 'rack1p1', 'myl6b-as1', 'kctd13-dt', 'linc02917', 'garin6', 'naa50p1', 'ttbk2-as1', 'cdh3-as1', 'cfap95', 'linc03014', 'linc03008', 'fam136dp', 'akap13-as1', 'linc02997', 'psmd14-dt', 'garin4', 'gusbp18', 'ttc36-as1', 'linc02972', 'xndc1cp', 'glipr1-as1', 'pdcd6-dt', 'tars1-dt', 'klc1-as1', 'linc02923', 'linc02925', 'zbed9p1', 'golga6fp', 'etnk1-dt', 'golga6l24p', 'gbx2-as1', 'myo1d-dt', 'adgrb3-dt', 'linc02933', 'gnb1-dt', 'garin3', 'cmklr2-as', 'tbx3-as1', 'cphxl2', 'pde3a-as1', 'pcdh10-dt', 'lefty3p', 'marchf11-dt', 'tmem109-dt', 'epic1', 'whammp4', 'linc03015', 'get1p1', 'cfap418', 'vnn3p', 'syt15-as1', 'spopl-dt', 'linc02910', 'garin5a', 'ccz1p1', 'mrfap1p1', 'c10orf67-as1', 'mta1-dt', 'heatr5a-dt', 'znf692-dt', 'cd300ld-as1', 'ppp1cb-dt', 'linc03009', 'ica1-as1', 'rwdd3-dt', 'spen-as1', 'yae1-dt', 'linc02959', 'errfi1-dt', 'bhlhe22-as1', 'tomt', 'or2w1-as1', 'aga-dt', 'ywhah-as1', 'exo5-dt', 'clec4op', 'linc03019', 'mirlet7ihg', 'sorl1-as1', 'cripak', 'bola3-dt', 'linc02978', 'chek2p7', 'zdhhc12-dt', 'map3k5-as2', 'emsy-dt', 'mir142hg', 'gvqw1', 'prkcz-dt', 'rbm33-dt', 'cfap100-dt', 'cd109-as1', 'fmnl1-as1', 'atp6ap1-dt', 'snx10-as1', 'dym-as1', 'trpc6p3', 'ankrd44-dt', 'linc03013', 'kmt2cp1', 'prpf31-as1', 'hlcs-as1', 'tsku-as1', 'zkscan8p1', 'golga7b-dt', 'rpl30-as1', 'mir3147hg', 'phb1p16', 'nudt16-dt', 'mdn1-as1', 'sod1-dt', 'virma-dt', 'linc03012', 'linc03004', 'linc02976', 'eci1-as1', 'prpf19-dt', 'cop1-dt', 'ankhd1-dt', 'msantd2-as1', 'ctglf8p', 'cfap53p1', 'nbpf7p', 'prr15-dt', 'ctnna1-as1', 'linc03026', 'entpd4-dt', 'phb1p3', 'brinp3-dt', 'mir3667hg', 'tmem184c-dt', 'mlf1-dt', 'garin5b', 'efhd2-as1', 'dgat2-dt', 'c4orf46p1', 'smarca2-as1', 'ndufv1-dt', 'fam136gp', 'linc02955', 'fam21d', 'esam-as1', 'zpr1p1', 'mtch1p2', 'linc03023', 'linc02939', 'linc02929', 'wdr35-dt', 'magea5p', 'cep72-dt', 'znf277-as1', 'linc02962', 'ercc6-pgbd3', 'atp11b-dt', 'linc02937', 'linc02991', 'bach1-it1', 'pigo-as1', 'pdgfa-dt', 'abca3p1', 'ing2-dt', 'linc03003', 'phb1p17', 'tprx2', 'linc02968', 'linc02965', 'dync1li2-dt', 'mfsd4b-dt', 'linc02969', 'linc02958', 'cacng2-dt', 'magi2-it1', 'pnn-as1', 'nepro-as1', 'tbc1d4-as1', 'wwp1-as1', 'fam13b-as1', 'anxa2r-ot1', 'ehbp1-as1', 'ints15', 'itga2-as1', 'eva1cp5', 'garin3p1', 'phb1p9', 'smim45', 'sybu-as1', 'cadm1-as1', 'epc1-as1', 'acaa2p1', 'rpl7ap79', 'klc2-as1', 'ankrd42-dt', 'mphosph10p3', 'oclm', 'mrnip-dt', 'tpbgl-as1', 'rpl6p23', 'trpc6p4', 'linc02979', 'slc20a1-dt', 'mindy2-dt', 'cd44-dt', 'fxyd6-as1', 'trim7-as2', 'patl1-dt', 'hsdl2-as1', 'lrp2bp-as1', 'rack1p2', 'adam7-as2', 'ppp1r15b-as1', 'golga6l25p', 'znf567-dt', 'fam136cp', 'npy2r-as1', 'rmel3', 'wdtc1-dt', 'map9-as1', 'kcnj5-as1', 'itpr2-as1', 'usp12-dt', 'ttc12-dt', 'linc02990', 'pbx3-dt', 'macc1-dt', 'krbox5', 'kmt2cp4', 'msantd3p1', 'htr4-it1', 'epm2a-dt', 'linc02935', 'phb1p2', 'slco5a1-as1', 'linc02956', 'dnaaf11p1', 'linc02932', 'tle1-dt', 'gusbp19', 'linc03010', 'linc02961', 'stx5-dt', 'anxa2r-as1', 'h2az2-dt', 'linc02927', 'znf56p', 'rcan2-dt', 'slc25a28-dt', 'linc02993', 'nfatc2ip-as1', 'nalf2', 'linc02988', 'rpl7ap81', 'phb1p5', 'rpl6p32', 'lnmicc', 'bms1p4-agap5', 'uba6-dt', 'lrp8-dt', 'bend7-dt', 'fibcd1-as1', 'dennd3-as1', 'copb2-dt', 'c1orf50-as1', 'rsph1-dt', 'r3hdml-as1', 'spdye12', 'icmt-dt', 'linc02983', 'pak6-as1', 'dnah8-dt', 'sdhap4', 'kmt2cp3', 'gpatch11p1', 'cpvl-as2', 'chfr-dt', 'ubqln1-as1', 'gask1b-as1', 'linc02934', 'garin2', 'syt15b', 'phb1p11', 'idh3b-dt', 'tnfrsf10a-dt', 'myo1b-as1', 'phb1p14', 'mcph1-dt', 'golga6ep', 'slc2a1-dt', 'rai14-dt', 'cntnap5-dt', 'phb1p12', 'linc02980', 'c1orf134', 'cfap20dc-dt', 'ntmt2', 'lmx1b-dt', 'mtmr12p1', 'fthl18p', 'eogt-dt', 'uhrf1bp1l-dt', 'znf285cp', 'ndnf-as1', 'cfap119', 'hivep2-dt', 'fsip2lp', 'syt9-as1', 'lncbrm', 'slc26a5-as1', 'golm2p1', 'linc02566', 'cyp26c1-dt', 'btg2-dt', 'mrm3p1', 'sqle-dt', 'ppp5d1p', 'abcf2-h2bk1', 'smim44', 'linc02938', 'c12orf75-as1', 'ciao2ap1', 'gpm6a-dt', 'aqp7b', 'fam136ep', 'gucy2c-as1', 'linc02989', 'yju2b', 'linc02922', 'abr-as1', 'ckap2-dt', 'rplp0p9', 'cnpy2-as1', 'igsf22-as1', 'cttn-dt', 'baz2b-as1', 'cbr4-dt', 'selenoo-as1', 'akr1c8', 'gjd2-dt', 'cox10-dt', 'fbxo38-dt', 'samd4a-as1', 'dpp3-dt', 'linc02524', 'kmt2cp5', 'wapl-dt', 'nicn1-as1', 'znf747-dt', 'fam151b-dt', 'tnks2-dt', 'gjd3-as1', 'gtf3c2-as2', 'epha2-as1', 'ggt2p', 'trpc6p9', 'znf705ep', 'mir30dhg', 'tmx4-as1', 'arl14ep-dt', 'ccdc13-as2', 'slc18a2-as1', 'ctns-as1', 'smarcad1-dt', 'dennd2b-as1', 'trpc6p1', 'hspa5-dt', 'phb1p19', 'lim2-as1', 'prss47p', 'rnf139-dt', 'hla-as1', 'pramef16', 'med28-dt', 'rnf186-as1', 'nemp2-dt', 'znf285bp', 'pkd1-as1', 'linc02987', 'arhgef4-as1', 'rpl7ap76', 'tenm2-as1', 'palm2', 'nek2-dt', 'phb1p21', 'linc02912', 'rrbp1p1', 'linc02921', 'linc02971', 'fosl2-as1', 'tbc1d3jp', 'cenpbd2p', 'linc02919', 'rpl6p31', 'rnaseh1-dt', 'fn1-dt', 'linc03002', 'tmem155', 'znf652-as1', 'nhsl1-as1', 'prss23-as1', 'l1cam-as1', 'c2orf74-dt', 'slc12a2-dt', 'tex28p3', 'thbs2-as1', 'asah1-as1', 'slc66a2p1', 'slc16a4-as1', 'hexim2-as1', 'linc02911', 'linc02946', 'lhfpl7', 'nubpl-dt', 'linc02964', 'lrrc3b-as1', 'zranb2-dt', 'linc02954', 'adgra3p1', 'tmem123-dt', 'zbed9-as1', 'srsf8cp', 'rrs1-dt', 'gstt3p', 'fam25hp', 'zkscan8p2', 'linc02999', 'cln8-as1', 'ripk2-dt', 'linc02918', 'arid4b-it1', 'gpat4-as1', 'grk3-as1', 'chmp3-as1', 'gnao1-dt', 'h2al1mp', 'fam88c', 'dock7-dt', 'linc03018', 'tirap-as1', 'pcgf3-as1', 'avpr1b-dt', 'jakmip1-dt', 'adm-dt', 'steap1b-as1', 'uqcrb-as1', 'tilrls', 'ccdc90b-as1', 'cdh13-as1', 'taf12-dt', 'zbtb24-dt', 'dph1-as1', 'cbll1-as1', 'brpf3-as1', 'smim34', 'lce7a', 'ccdc54-as1', 'plppr5-as1', 'cfap210', 'cabp7-dt', 'ppp1r3b-dt', 'ubl7-dt', 'ube2h-dt', 'galnt7-dt', 'c9orf38', 'znf24tr', 'linc02977', 'tmem167ap2', 'chd1-dt', 'clxn', 'eola1-dt', 'mtus1-dt', 'zfand3-dt', 'cfap95-dt', 'eva1cp2', 'micall2-dt', 'nalf1', 'phb1p13', 'c4orf46p3', 'stx17-dt', 'cbr1-as1', 'spdye10', 'slx9', 'fam174a-dt', 'tmem11-dt', 'igsf3p1', 'eif5-dt', 'vopp1-dt', 'mapk8ip3-as1', 'pnisr-as1', 'bud13-dt', 'smim14-dt', 'arhgef17-as1', 'mad2l1-dt', 'atox1-as1', 'tox-dt', 'zbtb7c-as2', 'mrps35-dt', 'map7-as1', 'rplp0p12', 'ube2e3-dt', 'hilpda-as1', 'trpc6p2', 'linc02947', 'atp13a3-dt', 'tbce-as1', 'znf285dp', 'hccs-dt', 'ankrd65-as1', 'cplane1-as1', 'fktn-as1', 'bcl10-as1', 'phb1p8', 'tdh-as1', 'tafazzin', 'pom121l15p', 'cd101-as1', 'prdm10-dt', 'linc02915', 
        'mphosph10p7', 'phb1p1', 'tns2-as1', 'dock8-as2', 'igsf3p2', 'linc02963', 'mtch1p1', 'golga6gp', 'rabgef1p3', 'h3-7', 'fam9cp1', 'eva1cp1', 'rimoc1', 'eva1cp4', 'golga6l23p', 'rabgef1p2', 'prss59p', 'pdlim7-as1', 'eva1cp3', 'trabd-as1', 'plxnb3-as1', 'irs4-as1', 'cse1l-dt', 'qkila', 'rmrpp2', 'tollip-dt', 'rmrpp4', 'adgb-dt', 'acad9-dt', 'cfap107', 'ctdp1-dt', 'linc02966', 'linc02957', 'srp14-dt', 'rel-dt', 'fam88b', 'trpc6p7', 'rpl7ap78', 'adamts16-dt', 'camsap1-dt', 'ttc14-dt', 'hspa12a-as1', 'twf2-dt', 'zbtb46-as2', 'capn1-as1', 'trpc6p10', 'cabp1-dt', 'ptprd-dt', 'hps1-as1', 'nup107-dt', 'linc02994', 'magoh-dt', 'myh9-dt', 'uchl1-dt', 'fam88f', 'dmtf1-as1', 'sorbs2-as1', 'slco4a1-as2', 'micos10-dt', 'tm9sf5p', 'linc02950', 'linc03017', 'rabgef1p1', 'flrt2-as1', 'mphosph10p9', 'ccno-dt', 'cibar1-dt', 'dph5-dt', 'ddit4l-as1', 'epb41l1-as1', 'linc02924', 'larp4b-dt', 'osmr-dt', 'phlda1-dt', 'rpl7ap82', 'nalf1-it1', 'ahi1-dt', 'kmt2cp2', 'tmem161b-dt', 'mphosph10p1', 'spaca6-as1', 'h2bk1', 'linc03007', 'gpr155-dt', 'rpl7ap80', 'spaca7bp', 'znf691-dt', 'il6st-dt'}

    return set({i for i in x if i not in ignore_genes})


def main(ensembl_biomart_geneids_transcript_info,
         hgnc_complete_set,
         isoform_overrides_uniprot,
         isoform_overrides_at_mskcc,
         isoform_overrides_genome_nexus,
         isoform_overrides_at_oncokb,
         ensembl_biomart_canonical_transcripts_per_hgnc):
    # input files
    transcript_info_df = pd.read_csv(ensembl_biomart_geneids_transcript_info, sep='\t', dtype={'is_canonical':bool})
    transcript_info_df = transcript_info_df.drop_duplicates()
    uniprot = pd.read_csv(isoform_overrides_uniprot, sep='\t')\
        .rename(columns={'enst_id':'isoform_override'})\
        .set_index('gene_name'.split())
    mskcc = pd.read_csv(isoform_overrides_at_mskcc, sep='\t')\
        .rename(columns={'enst_id':'isoform_override'})\
        .set_index('gene_name'.split())
    custom = pd.read_csv(isoform_overrides_genome_nexus, sep='\t')\
        .rename(columns={'enst_id':'isoform_override'})\
        .set_index('gene_name'.split())
    oncokb = pd.read_csv(isoform_overrides_at_oncokb, sep='\t')\
        .rename(columns={'enst_id':'isoform_override'})\
        .set_index('gene_name'.split())
    hgnc_df = pd.read_csv(hgnc_complete_set, sep='\t', dtype=object)

    # Convert new column names to old stable column names. If this is not done properly, Genome Nexus and any other
    # downstream applications break
    # TODO: Update Genome Nexus to accept the latest HGNC column names so that remapping is not necessary.
    column_name_mapping = {'name': 'approved_name',
                           'symbol': 'approved_symbol',
                           'prev_symbol': 'previous_symbols',
                           'alias_symbol': 'synonyms',
                           'location': 'chromosome',
                           'entrez_id': 'entrez_gene_id',
                           'ena': 'accession_numbers',
                           'refseq_accession': 'refseq_ids',
                           'uniprot_ids': 'uniprot_id',
                           'ensembl_id': 'ensembl_gene_id'}
    hgnc_df.rename(columns=column_name_mapping, inplace=True)
    hgnc_df = hgnc_df[hgnc_df['approved_name'] != 'entry withdrawn'].copy()
    hugos = hgnc_df['approved_symbol'].unique()
    hgnc_df = hgnc_df.set_index('approved_symbol')
    # assume each row has approved symbol
    assert(len(hugos) == len(hgnc_df))

    # only test the cancer genes for oddities (these are very important)
    cgs = set(pd.read_csv('common_input/oncokb_cancer_genes_list_20170926.txt',sep='\t')['Hugo Symbol'])
    # each cancer gene stable id should have only one associated cancer gene symbol
    assert(transcript_info_df[transcript_info_df.hgnc_symbol.isin(cgs)].groupby('gene_stable_id').hgnc_symbol.nunique().sort_values().nunique() == 1)
    # each transcript stable id always belongs to only one gene stable id
    assert(transcript_info_df.groupby('transcript_stable_id').gene_stable_id.nunique().sort_values().nunique() == 1)

    # create hgnc_symbol to gene id mapping
    # ignore hugo symbols from ensembl data dump (includes prev symbols and synonyms)
    syns = hgnc_df.synonyms.str.strip('"').str.split("|").dropna()
    syns = set(itertools.chain.from_iterable(syns))
    previous_symbols = hgnc_df.previous_symbols.str.strip('"').str.split("|").dropna()
    previous_symbols = set(itertools.chain.from_iterable(previous_symbols))

    # there is overlap between symbols, synonyms and previous symbols
    # therefore use logic in above order when querying
    # assert(len(syns.intersection(previous_symbols)) == 0) #329
    # assert(len(set(hugos).intersection(syns)) == 0) # 495
    # assert(len(set(hugos).intersection(previous_symbols)) == 0) #227

    # all cancer genes and hugo symbols in ensembl data dump should be
    # contained in hgnc approved symbols and synonyms
    # c12orf9 is only in sanger's cancer gene census and has been withdrawn
    assert(len(lowercase_set(set(cgs)) - set(['c12orf9']) - lowercase_set(set(hugos).union(syns).union(previous_symbols))) == 0)
    no_symbols_in_hgnc = lowercase_set(transcript_info_df.hgnc_symbol.dropna().unique()) - lowercase_set(set(hugos).union(syns).union(previous_symbols))
    assert(len(ignore_certain_genes(ignore_rna_gene(no_symbols_in_hgnc))) == 0)

    transcript_info_df = transcript_info_df.set_index('hgnc_symbol')
    # for testing use
    # NSD3 replaces WHSC1L1
    # AATF has uniprot canonical transcript, not hgnc ensembl gene id, but
    # there are multiple in ensembl data dump
    # hugos = ['KRT18P53', 'NSD3', 'AATF']

    # TODO Optimize this part, as this part takes most time
    one_transcript_per_hugo_symbol = pd.Series(hugos).apply(lambda x:
        pd.Series(
            [
                get_ensembl_canonical_transcript_id_from_hgnc_then_ensembl(transcript_info_df, x, hgnc_df, 'gene_stable_id'),
                get_ensembl_canonical_transcript_id_from_hgnc_then_ensembl(transcript_info_df, x, hgnc_df, 'transcript_stable_id'),
                get_overrides_transcript([custom], transcript_info_df, x, hgnc_df),
                get_overrides_transcript([uniprot, custom], transcript_info_df, x, hgnc_df),
                get_overrides_transcript([oncokb, mskcc, uniprot, custom], transcript_info_df, x, hgnc_df),
            ],
            index="""
            ensembl_canonical_gene
            ensembl_canonical_transcript
            genome_nexus_canonical_transcript
            uniprot_canonical_transcript
            mskcc_canonical_transcript
            """.split()
        )
    )
    one_transcript_per_hugo_symbol.index = hugos
    one_transcript_per_hugo_symbol.index.name = 'hgnc_symbol'

    # merge in other hgnc fields
    merged = pd.merge(one_transcript_per_hugo_symbol.reset_index(), hgnc_df.reset_index(), left_on='hgnc_symbol', right_on='approved_symbol')
    del merged['approved_symbol']
    del merged['ensembl_gene_id']

    # Replace '|' to ', ' to be in the correct format for Genome Nexus
    # TODO: Update Genome Nexus to accept the latest HGNC format so that replacement is not necessary.
    merged.replace({'\|': ', '}, inplace=True, regex=True)

    # Write file
    merged.to_csv(ensembl_biomart_canonical_transcripts_per_hgnc, sep='\t', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ensembl_biomart_geneids_transcript_info",
                        help="tmp/ensembl_biomart_geneids.transcript_info.txt")
    parser.add_argument("hgnc_complete_set",
                        help="common_input/hgnc_complete_set_20210218.txt")
    parser.add_argument("isoform_overrides_uniprot",
                        help="common_input/isoform_overrides_uniprot.txt")
    parser.add_argument("isoform_overrides_at_mskcc",
                        help="common_input/isoform_overrides_at_mskcc_grch37.txt or common_input/isoform_overrides_at_mskcc_grch38.txt")
    parser.add_argument("isoform_overrides_genome_nexus",
                        help="common_input/isoform_overrides_genome_nexus.txt")
    parser.add_argument("isoform_overrides_at_oncokb",
                        help="common_input/isoform_overrides_at_oncokb.txt")
    parser.add_argument("ensembl_biomart_canonical_transcripts_per_hgnc",
                        help="tmp/ensembl_biomart_canonical_transcripts_per_hgnc.txt")
    args = parser.parse_args()

    main(args.ensembl_biomart_geneids_transcript_info,
         args.hgnc_complete_set,
         args.isoform_overrides_uniprot,
         args.isoform_overrides_at_mskcc,
         args.isoform_overrides_genome_nexus,
         args.isoform_overrides_at_oncokb,
         args.ensembl_biomart_canonical_transcripts_per_hgnc)
