import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.impute import KNNImputer


def pre_process():
    kepler = pd.read_csv('./dataset/Kepler Objects of Interests.csv', on_bad_lines='skip')

    print("kepler prev attributes: " + str(kepler.columns.size))
    print("kepler prev rows: " + str(len(kepler)))
    kepler.drop(
        columns=['rowid', 'kepid', 'kepler_name', 'koi_vet_stat', 'koi_vet_date', 'koi_pdisposition', 'koi_score',
                 'koi_disp_prov', 'koi_comment', 'koi_time0bk', 'koi_time0bk_err1', 'koi_time0bk_err2', 'koi_fittype',
                 'koi_limbdark_mod', 'koi_parm_prov', 'koi_count', 'koi_tce_plnt_num', 'koi_tce_delivname',
                 'koi_trans_mod', 'koi_model_dof', 'koi_datalink_dvr', 'koi_datalink_dvs', 'koi_sparprov'],
        inplace=True)

    kepler['koi_disposition'].replace(
        {"FALSE POSITIVE": -1, "CONFIRMED": 1, "CANDIDATE": 0},
        inplace=True)

    thresh = len(kepler) * .5
    kepler.dropna(thresh=thresh, axis=1, inplace=True)  # remove columns with less than 70% of not nan values

    nunique = kepler.nunique()  # series with number of unique value for each column
    cols_unique_drop = nunique[nunique == 1].index  # indexes of columns with value of nunique == 1
    kepler.drop(cols_unique_drop, axis=1, inplace=True)

    kepler.drop_duplicates(subset='kepoi_name', keep='first')  # remove rows with duplicate value of kepoi_name column

    kepler = kepler[kepler.columns.drop(list(kepler.filter(regex='err')))]  # remove columns that contains err in attribute name
    kepler = kepler[kepler.columns.drop(list(kepler.filter(regex='lim')))]  # remove columns that contains lim in attribute name

    thresh = kepler.columns.size * .8
    kepler.dropna(thresh=thresh, axis=0, inplace=True)  # remove columns with less than 70% of not nan values

    kepler.to_csv('./dataset/pp_dataset/kepler_nocorr.csv')

    # remove attributes with a value of corr_m > 0.95 (see on the visual correlation matrix)
    kepler.drop(columns=['koi_fwm_sra', 'koi_fwm_sdec', 'koi_gmag', 'koi_rmag', 'koi_imag', 'koi_zmag', 'koi_jmag',
                         'koi_hmag', 'koi_kmag', 'koi_ldm_coeff2'], inplace=True)

    print("kepler next attributes: " + str(kepler.columns.size))

    kepler.to_csv('./dataset/pp_dataset/kepler.csv')

    kepler2 = kepler.drop(columns=['kepoi_name', 'koi_disposition'])

    imputer = KNNImputer(n_neighbors=5, weights='uniform', metric='nan_euclidean')
    kepler_filled = pd.DataFrame(imputer.fit_transform(kepler2), columns=kepler2.columns)

    print(kepler_filled.isnull().sum())

    name_col = kepler['kepoi_name']
    disposition_col = kepler['koi_disposition']
    kepler_filled = kepler_filled.join(name_col)
    kepler_filled = kepler_filled.join(disposition_col)

    kepler_filled.to_csv('./dataset/pp_dataset/kepler_filled.csv')

    return kepler
