import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# RADAR CHART
def _invert(x, limits):
    """inverts a value x on a scale from
    limits[0] to limits[1]"""
    return limits[1] - (x - limits[0])

def _scale_data(data, ranges):
    """scales data[1:] to ranges[0],
    inverts if the scale is reversed"""
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
#         st.write(d,y1,y2)
        assert (y1 <= d <= y2) or (y2 <= d <= y1)
    x1, x2 = ranges[0]

    d = list(data)[0]
    if x1 > x2:
        d = _invert(d, (x1, x2))
        x1, x2 = x2, x1
    sdata = [d]
    for d, (y1, y2) in zip(data[1:], ranges[1:]):
        if y1 > y2:
            d = _invert(d, (y1, y2))
            y1, y2 = y2, y1
        try:
            sdata.append((d-y1) / (y2-y1) 
                         * (x2 - x1) + x1)
        except:
            sdata.append(0)
    return sdata

class ComplexRadar():
    def __init__(self, fig, variables, ranges, COLOR_TXT,
                 n_ordinate_levels=6,drill=False):
        
        angles = np.arange(0, 360, 360./len(variables))

        axes = [fig.add_axes([0.1,0.1,0.9,0.9],polar=True,
                label = "axes{}".format(i)) 
                for i in range(len(variables))]
        l, text = axes[0].set_thetagrids(angles, 
                                         labels=['DIST\n(m)' if x=='Distanza totale' else 
                                                 'DIST\n(m\min)' if x=='Drel' else
                                                 x.replace(' ','\n').replace('power','').replace('acc','').replace('speed','') 
                                                 for x in variables])
#                                          labels=[x.replace(' ','\n') if x!='Drel' else 
#                                                  'DIST/min\n(m)' for x in variables])
        [txt.set_rotation(angle-90) for txt, angle 
             in zip(text, angles)]
        for ax in axes[1:]:
            ax.patch.set_visible(False)
            ax.grid(axis= 'both',lw=0.8,alpha=0.4,color='black')
            #ax.grid(axis= 'x',lw=0.1,alpha=0.01,color='black')
            ax.xaxis.set_visible(False)
        for i, ax in enumerate(axes):
            grid = np.linspace(*ranges[i], 
                               num=n_ordinate_levels)
            if drill == False:
                gridlabel = ["{:.0f}".format(round(x,2)) 
                             for x in grid]
            else:
                gridlabel = ["{:.1f}".format(round(x,2)) 
                             for x in grid]
            if ranges[i][0] > ranges[i][1]:
                grid = grid[::-1] # hack to invert grid
                          # gridlabels aren't reversed
            gridlabel[0] = "" # clean up origin
            ax.set_rgrids(grid, labels=gridlabel,
                         angle=angles[i], fontsize=13,color=COLOR_TXT)
            ax.spines["polar"].set_visible(True)
            ax.set_ylim(*ranges[i])
        # variables for plotting
        self.angle = np.deg2rad(np.r_[angles, angles[0]])
        self.ranges = ranges
        self.ax = axes[0]
    def plot(self, data, label, COLOR_TXT, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.plot(self.angle, np.r_[sdata, sdata[0]], label=label, *args, **kw)
        self.ax.legend(ncol=2,fontsize=18,bbox_to_anchor=(0.5,-0.21),fancybox=True,framealpha=0.2,loc='center',labelcolor=COLOR_TXT)
        self.ax.tick_params(axis='x', labelsize=15, pad=55,colors=COLOR_TXT)
    def fill(self, data, *args, **kw):
        sdata = _scale_data(data, self.ranges)
        self.ax.fill(self.angle, np.r_[sdata, sdata[0]], *args, **kw)


def drills_comp_radar_chart(json_,lst_drill_sel,dict_rename):

    COLOR_TXT = 'black'
    
    lst_val = []
    for drill in lst_drill_sel:
        lst_val.append(json_[drill])
    df_ = pd.DataFrame(lst_val,index=lst_drill_sel).T.fillna(0).rename(index=dict_rename).loc[dict_rename.values()]

    ## Aboslute values
    variables = [x for x in list(df_.T) if '/min)' not in x and x != 'Exposure (min)']
    
    min_max_per_variable = df_.T[variables].describe().T[['min', 'max']]
    min_max_per_variable['max'] = [ma if mi<ma else ma+1 for ma,mi in zip(min_max_per_variable['max'],min_max_per_variable['min'])]
    min_max_per_variable['min'] = min_max_per_variable['min'].apply(lambda x: x*0.1)
    min_max_per_variable['max'] = min_max_per_variable['max'].apply(lambda x: math.ceil(x)*1.4)

    ranges = list(min_max_per_variable.itertuples(index=False, name=None))

    fig1 = plt.figure(figsize=(10, 10))
    radar = ComplexRadar(fig1, variables, ranges, COLOR_TXT,drill=True)
    for col in lst_drill_sel:
        radar.plot(df_.loc[variables][col],label=col,COLOR_TXT=COLOR_TXT,ls='-',marker='o',lw=4,ms=10,alpha=0.8)
        radar.fill(df_.loc[variables][col], alpha=0.3)
    plt.title('Absolute values',fontsize=35, y=1.18,color=COLOR_TXT)
    fig1.tight_layout()
    
    
    ## Relative values
    variables = [x for x in list(df_.T) if '/min)' in x]
    
    min_max_per_variable = df_.T[variables].describe().T[['min', 'max']]
    min_max_per_variable['max'] = [ma if mi<ma else ma+1 for ma,mi in zip(min_max_per_variable['max'],min_max_per_variable['min'])]
    min_max_per_variable['min'] = min_max_per_variable['min'].apply(lambda x: x*0.1)
    min_max_per_variable['max'] = min_max_per_variable['max'].apply(lambda x: math.ceil(x)*1.4)

    ranges = list(min_max_per_variable.itertuples(index=False, name=None))

    # plotting
    fig2 = plt.figure(figsize=(10, 10))
    # sns.set_style('darkgrid')
    radar = ComplexRadar(fig2, variables, ranges, COLOR_TXT,drill=True)
    for col in lst_drill_sel:
        radar.plot(df_.loc[variables][col],label=col,COLOR_TXT=COLOR_TXT,ls='-',marker='o',lw=4,ms=10,alpha=0.8)
        radar.fill(df_.loc[variables][col], alpha=0.3)
    plt.title('Relative values',fontsize=35, y=1.18,color=COLOR_TXT)
    fig2.tight_layout()
    
    return fig1,fig2,df_