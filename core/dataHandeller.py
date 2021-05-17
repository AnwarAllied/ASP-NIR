# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .models import Spectrum, NirProfile
from chartjs.colors import next_color

def datasheet2spec(file,pk,filename):
    profile=NirProfile.objects.get(pk=pk)
    filetype=filename.split('.')[-1]
    if filetype in ['xlsx','xls']:
        try:
            exf=pd.ExcelFile(file)
            # upload the data from the 1st sheet: 
            sh1 = pd.read_excel(exf, exf.sheet_names[0],index_col=False)
            x_axis=list(map(float,list(sh1)[1:]))
            label1=sh1[list(sh1)[0]]
            dataset=np.array([sh1[list(sh1)[i+1]].values.tolist() for i in range(len(x_axis))]).T
            color_generator =next_color()
            xmin=min(x_axis)
            xmax=max(x_axis)
            for i in range(len(dataset)):
                S = Spectrum(
                    origin = '%s %s %s %s' % (filename.split('-')[0],label1[i],list(sh1)[0],filename.split('-')[-1].split('.')[0]),
                    code = 'WM%dV%dX%dN%d' % (np.mean(dataset[i]),np.var(dataset[i]),np.max(dataset[i]),np.min(dataset[i])),
                    color = '#%02X%02X%02X' % tuple(next(color_generator)),
                    y_axis = str(dataset[i].tolist())[1:-1],
                    x_range_max = xmax,
                    x_range_min = xmin,
                    nir_profile = profile
                )
                S.save()
                print("spectrum",i, 'saved')
        except Exception as e:
            return False , 'Error while processing '+filename+ ' :'+e.__str__()
    elif filetype=='csv':
        try:
            sh1 = pd.read_csv(file)
            # print('len-index:',len(sh1.index))
            if len(sh1.index)==256:
                file.seek(0)
                sh2 = pd.read_csv(file,header=1)
                print('sh2-index:',sh2.index)
                # print('values:',sh1['Column 1'][27:].values.tolist())
                y_axis = list(map(float, sh2['Column 1'][27:].values.tolist()))
                x_axis = list(map(float, sh2['Scan Config Name:'][27:].values.tolist()))
            # label1=sh1[list(sh1)[0]]
            # dataset=np.array([sh1[list(sh1)[i+1]].values.tolist() for i in range(len(x_axis))]).T
            # print('n-dataset:',len(dataset))
            else:
                y_axis = list(map(float, sh1['Column 1'][21:].values.tolist()))
                x_axis = list(map(float, sh1['Method:'][21:].values.tolist()))
            color_generator =next_color()
            xmin=min(x_axis)
            xmax=max(x_axis)
            S = Spectrum(
                origin = '%s %s' % (filename.split('_')[0],filename.split('_')[-1].split('.')[0]),
                code = 'WM%dV%dX%dN%d' % (np.mean(y_axis),np.var(y_axis),np.max(y_axis),np.min(y_axis)),
                color = '#%02X%02X%02X' % tuple(next(color_generator)),
                y_axis = str(y_axis)[1:-1],
                x_range_max = xmax,
                x_range_min = xmin,
                nir_profile = profile
            )
            S.save()
        except Exception as e:
            return False , 'Error while processing '+filename+ ' :'+e.__str__()
    return True, 'successfuly uploads'

def detect_xls_profile(xls):
    """
    To detect the format of the spectral content in the xls file:

    The file name format: "ORIGIN ORIGINSUB1 ORIGINSUB2 ... - LABLE1 LABLE2 ... - REFFERANCE Note... .xlsx"
    ORIGIN: Wheat, Soybean
    ORIGINSUB1: Granded, Flour
    LABLE1: Protein, Brix
    LABLE2: Moisture, ...
    REFFERANCE: ASP, Alan Ames
    Note: 1_20201126_120750
    A: NIRvaScan format: single sheet & single spectrum in colB after row22.
    B: One sheet & one index format: 1st row for x-axis data and 1st col for label (e.g. protein level).
    C: One sheet & multi index formats (for labels): as B and 2nd, 3rd col for lables (e.g. protein and moisture).
    D: Multi-sheet format

    """
    # extract all the infos from the file name
    # xls = 'Wheat Granded Flour-Protein Brix Moisture-ASP Alan_Ames-1_20201126_120750.xls'
    xls = xls.split('-')
    a = xls[0].split()
    origin = a[0]
    originsubs = [a[i] for i in range(1, len(a))]
    labels = xls[1].split()
    references = xls[2].split()
    note = xls[3].split('.')[0]

    # detect the type of file
    data_labels, content_labels, X_dataset, Y_sepctra_dataset, Y_content_dataset = [], [], [], [], []
    tb = pd.ExcelFile(xls, engine='openpyxl')
    sheet_names = tb.sheet_names
    df = pd.read_excel(tb, sheet_names, header=None)
    for sheet in sheet_names:  # we assume there are several sheets
        if pd.read_excel(tb, tb.sheet).values[:]:
            if str(df[sheet].loc[1, 1]).isalpha():
                if str(df[sheet].loc[1, 2]).isalpha():  # C, file like narcatic_spectra_new
                    i = 1
                    while str(df[sheet].loc[1, i]).isalpha():
                        content_labels.append(df[sheet].loc[1, i])
                        Y_content_dataset.append(df[sheet].values[1:, i])
                        i += 1  # we assume there are a lot of content labels
                    data_labels.append(df[sheet].values[:, 0])  # if all the labels of spectra are in the first column
                else:  # A
                    data_labels.append(labels)  # we assume the spectrum label is in the filename
                    Y_sepctra_dataset.append(df[sheet].values[23:, 1])  # all data are in 1B after row22
            else:  # B
                X_dataset.append(df[sheet].values[0, 1:])  # we assume cell[0,0] stocks (label\x-data)
                Y_sepctra_dataset.append(df[sheet].values[1:, 1:])

# def figure_2(*args):
#     print(args)
#     fig, ax = plt.subplots()
#     ax.plot([1, 3, 4], [3, 2, 5])
#     return fig