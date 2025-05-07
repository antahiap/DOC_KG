from constants import ABBS_FILE
from file_reader import Doco
from pathlib import Path


if __name__ == "__main__":

    abbs_src = Doco(Path(ABBS_FILE))
    abbs_tbls = abbs_src.extract_table('dataframe')

    i = 0
    for ii in range(i, len(abbs_tbls)):
        tbl = abbs_tbls[ii]
        print(i, tbl.shape)

        