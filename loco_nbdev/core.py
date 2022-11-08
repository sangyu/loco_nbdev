# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/plotTools.ipynb.

# %% auto 0
__all__ = ['correlationPlot', 'setFont', 'plotContrasts', 'savePlots', 'saveDabestData']

# %% ../nbs/plotTools.ipynb 1
"""
Created on Tue Apr 13 16:39:17 2021

@author: xusy
"""
import scipy
import matplotlib as plt
import pandas as pd
import dabest
import numpy as np

# %% ../nbs/plotTools.ipynb 2
def correlationPlot(x, y, ax = None):
    import scipy
    if ax == None:
        ax = plt.gca()
    ax.plot(x, y, 'r.')
    
    r, p = scipy.stats.pearsonr(x, y)
    print('pearson\'r ' + str(r) +  ', p value = ' + str(p))
    return ax, r, p 




# %% ../nbs/plotTools.ipynb 3
def setFont(fontSelection, fontSize, fontWeight = 'normal'):
    import matplotlib as mpl
    from matplotlib import rcParams
    # mpl.font_manager._rebuild()
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = [fontSelection]
    rcParams['font.size'] = fontSize 
    rcParams['font.weight'] = fontWeight



# %% ../nbs/plotTools.ipynb 4
def plotContrasts(df, y, colorBy, compareBy, groupBy = 'Temperature', reverseCompareBy = False, reverseGroupBy = False, customPalette = None, pairedState = False, fontSize = 14, plot_kwargs = dict()):
    setFont('Source Sans Bold', fontSize)
    groups = np.unique(df[groupBy].astype(str))
    if reverseGroupBy:
        groups = groups[::-1]

    compares = np.unique(df[compareBy].astype(str))
    if reverseCompareBy:
        compares = compares[::-1]
    df['newPlotColumn'] = df[groupBy].astype(str) + '  ' + df[compareBy]
    idxList = np.atleast_2d(groups[0]+'  ' +compares)


    for i in range(1, len(groups)):
        idxList = np.append(idxList, [groups[i]+'  ' +compares], axis = 0)
    idxTuple = tuple([tuple(l) for l in idxList])

    
    dabestContrastData = dabest.load(df,
                           x='newPlotColumn', # the default for this test config is to group flies by genotype
                           y=y,
                           idx=idxTuple,
                           paired=False
                          )
    dabestContrastFig = dabestContrastData.mean_diff.plot( color_col=colorBy, custom_palette = customPalette, **plot_kwargs)
    print(dabestContrastData.hedges_g)
    if len(np.unique(df[groupBy]))==1:
        flatListIdxC = [item.split('  ')[1] for item in idxTuple]
        flatListIdxG = [item.split('  ')[0] for item in idxTuple]
    else:
        flatListIdxC = [item.split('  ')[1] for t in idxTuple for item in t]
        flatListIdxG = [item.split('  ')[0] for t in idxTuple for item in t]
    print(flatListIdxC)
    print(flatListIdxG)
#     if np.max([len(item) for item in flatListIdxC])>4:
#         dabestContrastFig.axes[0].set_xticklabels(flatListIdxC, rotation = 45, ha="right")
#     else:
#         dabestContrastFig.axes[0].set_xticklabels(flatListIdxC, rotation = 0, ha="center")
        
    ylim = dabestContrastFig.axes[0].get_ylim()
    for i in range(0, len(groups)):
        xpos = (len(compares)-1)/2 + (i)*len(compares)
        dabestContrastFig.axes[0].text(xpos, ylim[1]*1.05, groups[i], ha="center")
        dabestContrastFig.tight_layout()
        dabestContrastFig.axes[0].plot([0 + i*len(compares), len(compares)-1 + i*len(compares)], [ylim[1], ylim[1]], 'k')
    
    return dabestContrastFig, dabestContrastData
    



# %% ../nbs/plotTools.ipynb 5
def savePlots(figure, fileName, figureID = '', fDPI = 300):
    figure.savefig(fileName +figureID +'.png',transparent=False, bbox_inches='tight', dpi=fDPI, pad=0.1, w_pad=0.5, h_pad=1.0)
    figure.savefig(fileName +figureID +'.svg', bbox_inches='tight', pad=0.1, w_pad=0.5, h_pad=1)
#       


# %% ../nbs/plotTools.ipynb 6
def saveDabestData(contrast, fileName, exptDataSource, figureID = '', unit = ''):
    
    #2022/01/25 changed the format of output file added _summary
    
    mStats = contrast.mean_diff.results
    gStats = contrast.hedges_g.results
    meanDiffRounded = mStats.round(2)
    hedgesGRounded = gStats.round(2)
    meanDiffRounded.to_csv(fileName +figureID + '_meanDiff.csv')
    hedgesGRounded.to_csv( fileName +figureID + '_hedgesG.csv')

    meanDiffRounded['comparison_number'] = range(len(meanDiffRounded))
    hedgesGRounded['comparison_number'] = range(len(hedgesGRounded))
    resultsMerged = pd.merge(meanDiffRounded, hedgesGRounded, on='comparison_number')
    resultsMerged.columns = resultsMerged.columns.str.replace('_x', '_MD')
    resultsMerged.columns = resultsMerged.columns.str.replace('_y', '_HG')

    results1 = pd.merge(meanDiffRounded[['control', 'test', 'control_N', 'test_N', 'comparison_number']] ,
                        resultsMerged[['difference_MD', 'comparison_number','ci_MD', 
                                       'bca_low_MD', 'bca_high_MD',
       'bca_interval_idx_MD', 'pct_low_MD', 'pct_high_MD',
       'pct_interval_idx_MD',
       'difference_HG', 'ci_HG', 'bca_low_HG', 'bca_high_HG',
       'bca_interval_idx_HG', 'pct_low_HG', 'pct_high_HG',
       'pct_interval_idx_HG']], on='comparison_number')
    

    summaryResults = pd.merge(results1, meanDiffRounded.iloc[:, 17:26], on = 'comparison_number')

    cols = list(summaryResults)
    # move the column to head of list using index, pop and insert
    cols.insert(0, cols.pop(cols.index('comparison_number')))
    summaryResults = summaryResults.loc[:, cols]
    if figureID:
        summaryResults['comparison_number'] =  figureID + '_' + summaryResults['comparison_number'].astype(str)
    summaryResults.to_csv(fileName +figureID + '_summary.csv')
    
    
    f= open(fileName+"ES_Sentences.txt","w+")
    print('Saving stats to ' + fileName +figureID +"ES_Sentences.txt")
    f.writelines('Location of data: \n' + exptDataSource + '\n\n\n')
    print('\n' + figureID + '\n\n')
    f.writelines('\n' + figureID + '\n\n')

    for i in range (0, len(mStats)):
        if mStats.difference[i] >0:
            comp = 'higher than '
        else:
            comp = 'lower than '

        meanDiffSentence = 'Test group ("' + mStats.loc[i, 'test'] \
            + '", sample size ' + str(mStats.loc[i, 'test_N'])\
                + ') is ' + comp + 'control group ("'   \
                    + mStats.loc[i, 'control'] + '", sample size ' \
                        + str(mStats.loc[i, 'control_N'])+  ') by ' \
                            + str(np.abs(mStats.loc[i, 'difference'].round(2))) + ' ' + unit\
                                + ' ('+ str(mStats.loc[i, 'ci']) +'% CI = [' \
                                    + str(mStats.loc[i, 'bca_low'].round(2)) + ', ' \
                                        + str(mStats.loc[i, 'bca_high'].round(2)) + '] ' + unit + ', p-value = ' \
                                            + str(mStats.iloc[i, -2].round(3))+', g = ' + str(gStats.loc[i, 'difference'].round(2))\
                                                + ').\nHypothesis test used is '\
                                                +' '.join(mStats.columns[-2].split('_')[1:3]) + '.\n'
                                                
                                                
                                                
                                                
        hedgesGSentence = 'Hedge\'s g for this comparison is ' + str(gStats.loc[i, 'difference'].round(2)) + ' '\
            + '('+ str(gStats.loc[i, 'ci']) +'% CI = [' \
                + str(gStats.loc[i, 'bca_low'].round(2)) \
                    + ', ' + str(gStats.loc[i, 'bca_high'].round(2)) + '] '+unit+').\n\n'

        print('Bootstrap '  + str(i+1))
        print(meanDiffSentence)
        print(hedgesGSentence)
        
        f.writelines('Bootstrap ' + str(i+1) + '\n')
        f.writelines(meanDiffSentence)
        f.writelines(hedgesGSentence)
    f.close()

    return summaryResults