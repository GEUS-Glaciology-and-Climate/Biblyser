"""
Biblyser (c) is a bibliometric workflow for evaluating the bib metrics of an 
individual or a group of people (an organisation).

Biblyser is licensed under a MIT License.

You should have received a copy of the license along with this work. If not, 
see <https://choosealicense.com/licenses/mit/>.
"""

import sys
import numpy as np
import pandas as pd
from collections import Counter
from textwrap import wrap
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

sys.path.append('../')
from BibCollection import getGenderDistrib, countByYear

    
#Import organisation from csv
org_df = pd.read_csv('output/out_organisation.csv')

#Import bibcollection from csv 
df = pd.read_csv('output/out_bibs.csv')

#Convert column items to appropriate objects
df['org_led'] = df['org_led'].astype('bool')
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
df['year'] = df['date'].dt.year

#Define bins
bin10=[0, 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99, 100]
bin25=[0, 1, 25, 50, 75, 99, 100]

#Define bin labels
l10 = ['0', '1-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', 
       '71-80', '81-90', '91-99', '100']
l25 = ['0%', '1-25%', '26-50%', '51-75%', '76-99%', '100%']

#Set color palettes
cold = ['#337BA7','#08589e','#2b8cbe','#4eb3d3','#7bccc4','#a8ddb5', '#ccebc5']
warm = ['#C85353','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026']


#------------------   Fetch and plot general publication stats ----------------


#Get count from first author publications
first = df.loc[df['org_led']==True]  
first_yr = countByYear(first)

#Get count from co-author publications
coauthor = df.loc[df['org_led']==False]  
co_yr = countByYear(coauthor)

#Merge and rename columns
co_yr['First author'] = first_yr['count']
all_yr = co_yr.rename(columns={'count' : 'Co-author'})

#Group journals
journals = df['journal'].groupby(df['journal']).agg({'count'}).sort_values(by=['count'], 
                                                                           ascending=True)
j10 = journals.tail(10)
others = len(list(journals['count'][:-10]))

#Affiliations of authorship
affiliations = list(df['affiliations'])
out1=[]
for a in affiliations:
    allc = a.split(', ')
    [out1.append(a) for a in allc]
out1 = Counter(out1).most_common()
aff_keys10 = [o[0] for o in out1[1:11]]
aff_vals10 = [o[1] for o in out1[1:11]]
aff_keys10.append('Others')
aff_vals10.append(sum(sorted(list(Counter(out1).values()))[11:]))
 
#Countries of authorship
countries = list(df['countries'])
out=[]
for c in countries:
    allc = c.split(', ')
    [out.append(a) for a in allc]
out = Counter(out).most_common()
co_keys10 = [o[0] for o in out[0:10]]
co_vals10 = [o[1] for o in out[0:10]]
co_keys10.append('Others')
co_vals10.append(sum(sorted(list(Counter(out).values()))[10:]))

#Prime subplots
fig1, ax1 = plt.subplots(1, 1, figsize=(10,10))
fig1.tight_layout(pad=4, h_pad=8, w_pad=0)
ax2 = ax1.inset_axes([0.2,0.47,0.3,0.2])                #Journals bar plt
ax3 = ax1.inset_axes([0.21,0.75,0.2,0.2])               #Pie #1
ax4 = ax1.inset_axes([0.54,0.75,0.2,0.2])               #Pie #2

#Set font styles and colour palettes
fontname='Arial'
title = 18
lfont1 = 14
lfont2 = 10
lfont3 = 7 
tfont = {'fontsize':10, 'color':'#5D5D5D'}
bar_col = ['#0C7BDC','#FFC20A', '#CA4646']
pie_col = ['#332288','#88CCEE','#44AA99','#117733','#999933','#DDCC77',
           '#CC6677','#882255','#AA4499','#6F3866','#DDDDDD']

#Plot year vs. authorships
all_yr.plot(kind='bar', stacked=False, color=[bar_col[0],bar_col[1]], ax=ax1)
ax1.set(ylim=(0,40), yticks=[0,10,20,30,40], xlabel='Date', 
        ylabel='Number of publications')

#Alter plot aesthetics
ax1.tick_params(axis='both', labelsize=tfont['fontsize'], labelcolor=tfont['color'])
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}')) 
  
#Set annotations
ax1.set_ylabel('Number of publications', labelpad=10, fontsize=lfont1)
ax1.set_xlabel('Date', labelpad=10, fontsize=lfont1)
ax1.legend(loc=4, fontsize=lfont2, framealpha=1,
           title='Publications by year')

#Plot popular journals 
ax2.barh([l*2 for l in np.arange(10)], list(j10['count']), color=bar_col[2])
ax2.set_yticks([l*2 for l in np.arange(10)])
labels = [ '\n'.join(wrap(l, 30)) for l in list(j10.index)]
ax2.set_yticklabels(labels, fontsize=lfont3)
ax2.tick_params(axis='x', labelsize=8, labelcolor=tfont['color'])
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.text(20, 0.5, f'Number of other journals: {others}', fontsize=lfont3)

#Plot top collaborator affiliations
p3,t3 = ax3.pie(aff_vals10, startangle=90, colors=pie_col, 
                wedgeprops={"edgecolor":"w",'linewidth':1})
legend_labels = [ '\n'.join(wrap(l, 30)) for l in aff_keys10]
ax3.legend(legend_labels, loc='center left', bbox_to_anchor=(-1.0, 0.5), 
           fontsize=lfont3)

#Plot top collaborator countries
p4,t4 = ax4.pie(co_vals10, startangle=90, colors=pie_col, 
                wedgeprops={"edgecolor":"w",'linewidth':1})
legend_labels = [ '\n'.join(wrap(l, 15)) for l in co_keys10]
ax4.legend(legend_labels, loc='center left', bbox_to_anchor=(-0.6, 0.5), 
           fontsize=lfont3)

#Plot summary table
ax4 = ax1.inset_axes([-0.02,0.38,0.4,0.1])
cells = [['Total publications', str(len(df.index))], 
         ['Organisation-led publications', str(len(first.index))], 
         ['Co-authored publications', str(len(coauthor.index))],
         ['Average citation count', str(int(np.nanmean(list(df['citations']))))],
         ['Average altmetrics', str(int(np.nanmean(list(df['altmetric']))))]]
table = ax4.table(cellText=cells, colWidths=[0.6,0.2], edges='horizontal',
                  cellLoc='left')
ax4.axis("off")
table.scale(1, 1.25)
table.auto_set_font_size(False)
table.set_fontsize(lfont3)

#Set annotations
plt.title('GEUS publications', fontsize=title)
ax1.text(1, 39.7, 'Top collaborators', fontsize=lfont1)
ax1.text(1, 27.2, 'Top journals', fontsize=lfont1)
ax1.text(1, 15.8, 'Summary statistics', fontsize=lfont1)

#Plot and save
plt.rcParams["font.family"] = fontname
plt.savefig('output/publication_stats.jpg', dpi=300)
# plt.show()
plt.close()

#------------   Publication lead and co-authorship by gender   ----------------


#Set font styles 
hfont = {'fontname':'Arial', 'fontsize':16}#, 'fontweight': 'bold'}
lfont1 = {'fontname':'Arial', 'fontsize':12, 'color':'#5D5D5D'}  
tfont = {'fontname':'Arial', 'fontsize':8, 'color':'#5D5D5D'}

#Get org gender from org papers
df1=pd.DataFrame()
for index, row in df.iterrows():
    f_led=0
    f_co=0
    m_led=0
    m_co=0
    genders = str(row['org_genders']).split(', ')
    if row['org_led']==True: 
        if genders[0]=='female':
            f_led=f_led+1
        else:
            m_led=m_led+1
        genders = genders[1:]
    
    for g in genders:
        if g=='female':
            f_co=f_co+1
        else:
            m_co=m_co+1  
    #Construct pandas series and append to dataframe
    series = pd.Series({'year': row['date'].year, 
                      'female_lead': f_led,
                      'male_lead': m_led, 
                      'female_co': f_co,
                      'male_co': m_co})
    df1 = df1.append(series, ignore_index=True)

#Group and sum by year
df2 = df1.groupby(['year']).agg({'female_lead':'sum','male_lead':'sum',
                           'female_co':'sum','male_co':'sum'})    
years = [int(y) for y in list(df2.index)]
x = list(range(len(years)))
x = [float(x1)*2 for x1 in x]
x = np.array(x)

#Prime plotting area
fig1 = plt.figure(figsize=(10,10))
gs = gridspec.GridSpec(2, 3, figure=fig1)
ax1 = plt.subplot(gs[:, 0])
gs.update(hspace=0)
ax2 = plt.subplot(gs[0, 1:])
ax3 = plt.subplot(gs[1, 1:], sharex=ax2)

#Plot as bars 
ax1.bar([0,1,3,4], [sum(list(df2['female_lead'])),
        sum(list(df2['male_lead'])),sum(list(df2['female_co'])),
        sum(list(df2['male_co']))], width=1, edgecolor='w', 
        color=[cold[2], warm[5], cold[4], warm[3]], align='center')     
ax2.bar(x-0.3, list(df2['female_lead']), width=0.6, color=cold[2], 
        align='center', label='Female lead author')
ax2.bar(x+0.3, list(df2['male_lead']), width=0.6, color=warm[5], 
        align='center', label='Male lead author')
ax3.bar(x-0.3, list(df2['female_co']), width=0.6, color=cold[4], 
        align='center', label='Female co-author')
ax3.bar(x+0.3, list(df2['male_co']), width=0.6, color=warm[3], 
        align='center', label='Male co-author')

#Set legends
[ax.legend(loc=2, fontsize=lfont1['fontsize']) for ax in [ax2, ax3]]

#Set x axes
ax1.set_xticks([0,1,3,4])
ax1.set_xticklabels(['Female\nlead', 'Male\nlead', 'Female\nco', 
                     'Male\nco'], **tfont)
ax2ytwin = ax2.twiny()
for ax in [ax2ytwin, ax3]:
    ax.set_xlim(0.6,x[-1]+1)
    ax.set_xticks(x[1:])
    ax.set_xticklabels(years[1:], rotation=45, **tfont)

#Set y axes
ax1.set_ylim(0,450)
ax1.set_yticks([0,100,200,300,400])
ax1.set_yticklabels(['0','100','200','300','400'], **tfont)
ax2xtwin = ax2.twinx()
for ax in [ax2, ax2xtwin]:
    ax.set_ylim(0,15)
    ax.set_yticks([0,3,6,9,12,15])
    ax.set_yticklabels(['0','3','6','9','12',''], **tfont)
ax3xtwin = ax3.twinx()
for ax in [ax3, ax3xtwin]:
    ax.set_ylim(0,50)
    ax.set_yticks([0,10,20,30,40,50])
    ax.set_yticklabels(['0','10','20','30','40',''], **tfont)

#Set plot grids   
[ax.set_axisbelow(True) for ax in [ax1,ax2,ax3]]
[ax.grid(color='gray', linestyle='dashed', axis='y') for ax in [ax1,ax2,ax3]]    

#Plot summary table of organisation
ax4 = ax1.inset_axes([0.15,0.943,0.4,0.1])
cells = [['Total female colleagues', str(list(org_df['guessed_gender']).count('female'))], 
         ['Total male collegues', str(list(org_df['guessed_gender']).count('male'))], 
         ['Professors', str(list(org_df['title']).count('Forskningsprofessor'))],
         ['Seniorforsker', str(list(org_df['title']).count('Seniorforsker'))],
         ['Forsker', str(list(org_df['title']).count('Forsker'))],
         ['Post-doctoral researchers', str(list(org_df['title']).count('Postdoc'))],  
         ['PhD students', str(list(org_df['title']).count('Ph.d.-studerende'))],
         ['Other staff', str(list(org_df['title']).count('Chefkonsulent') +
         list(org_df['title']).count('Statsgeolog') +  
         list(org_df['title']).count('AC-medarbejder') +  
         list(org_df['title']).count('Seniorrådgiver'))]]         
table = ax4.table(cellText=cells, colWidths=[1.3,0.2], edges='horizontal',
                  cellLoc='left', alpha=1, zorder=1)
ax4.axis("off")
table.scale(1, 1.25)
table.auto_set_font_size(False)
table.set_fontsize(tfont['fontsize'])

#Set labels and annotations
ax1.text(-0.4, 432, 'Organisation summary', fontsize=lfont1['fontsize'])
ax1.set_ylabel('Total publications', **lfont1)
ax2xtwin.set_ylabel('Number of publications (per year)', **lfont1, rotation=270)
ax2xtwin.yaxis.set_label_coords(1.08, 0)

#Plot and save
plt.rcParams["font.family"] = fontname
plt.tight_layout()
plt.savefig('output/publication_genders.jpg', dpi=300)   
plt.show()    


#----------  % female/male authorship in organisation-led papers   ------------


#Get only organisation-led papers
org_led = df.loc[df['org_led']==True] 

#Compute gender percentages in authorships
fauthors, mauthors, nbauthors = getGenderDistrib(org_led)

#Calculate bins for pie charts
fauthors_bin, b1 = np.histogram(fauthors, bin25, range=(bin25[0],bin25[-1])) 
mauthors_bin, b2 = np.histogram(mauthors, bin25, range=(bin25[0],bin25[-1])) 

#Prime subplots
fig1, (ax1, ax3) = plt.subplots(2, 1, figsize=(10,10))
fig1.tight_layout(pad=4, h_pad=8, w_pad=0)

#Set font styles and colour palettes
hfont = {'fontname':'Arial', 'fontsize':16}#, 'fontweight': 'bold'}
lfont1 = {'fontname':'Arial', 'fontsize':14} 
lfont2 = {'fontname':'Arial', 'fontsize':10} 
tfont = {'fontname':'Arial', 'fontsize':12, 'color':'#5D5D5D'}
afont = {'fontname':'Arial', 'fontsize':8} 


#Plot histograms
h1,e1 = np.histogram(fauthors, bins=bin10)
h2,e2 = np.histogram(mauthors, bins=bin10)

ax1.bar(list(range(0, (len(bin10)-1)*10, 10)), h1, width=10, 
        color=cold[0], edgecolor='white')
ax3.bar(list(range(0, (len(bin10)-1)*10, 10)), h2, width=10, 
        color=warm[0], edgecolor='white')

# ax1.hist(fauthors, bins=bin10, color=cold[0], edgecolor='white')
# ax3.hist(mauthors, bins=bin10, color=warm[0], edgecolor='white')

ax1.axvline(sum(fauthors)/len(fauthors), linewidth=2, color=cold[1])
ax3.axvline(sum(mauthors)/len(mauthors), linewidth=2, color=warm[-1])

#Plot pie charts
ax2 = ax1.inset_axes([0.45,0.3,0.65,0.65])
ax4 = ax3.inset_axes([-0.08,0.3,0.65,0.65])
p2,t2,a2 = ax2.pie(fauthors_bin, explode=(0.1, 0, 0, 0, 0, 0), labels=l25, 
                    colors=cold[1:],textprops=lfont2, autopct='%1.0f%%', 
                    startangle=90, wedgeprops={"edgecolor":"w",'linewidth':1},
                    pctdistance=0.5, labeldistance=1.05)
p4,t4,a4 = ax4.pie(mauthors_bin, explode=(0, 0, 0, 0, 0.1, 0), labels=l25, 
                    colors=warm[1:], textprops=lfont2, autopct='%1.0f%%', 
                    startangle=90, wedgeprops={"edgecolor":"w",'linewidth':1},
                    pctdistance=0.5, labeldistance=1.05)

#Set histogram plot parameters
for ax in [ax1,ax3]:
    ax.set_xlim(-5, (len(bin10)-1)*10)
    ax.set_ylim(0,60)
    ax.set_xticks([0,10,20,30,40,50,60,70,80,90,100,110])
    ax.set_xticklabels(l10, tfont)
    ax.set_yticklabels(ax.get_yticks(), tfont)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))   
    ax.set_ylabel('Number of publications', **lfont1)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
ax1.set_xlabel('% female authorship', **lfont1)
ax3.set_xlabel('% male authorship', **lfont1)

#Set pie plot parameters
for ax in [ax2,ax4]:
    ax.axis('equal')
for a in [a2,a4]:
    [text.set_color('#5D5D5D') for text in a]
    [text.set_fontsize(10) for text in a]
for at in [a2[0],a2[1],a2[2],a4[-1],a4[-2],a4[-3]]:
    at.set_color('white')

#Adjust pie chart label position
x,y = t4[0].get_position()
t4[0].set_position((x+0.1, y+0.05))
x,y = t4[1].get_position()
t4[1].set_position((x, y+0.1))
x,y = t2[5].get_position()
t2[5].set_position((x-0.1, y+0.1))
for p in [[p2,a2],[p4,a4]]:
    for patch, txt in zip(p[0], p[1]):
        ang = (patch.theta2 + patch.theta1) / 2.
        x = patch.r * 0.7 * np.cos(ang * np.pi / 180)
        y = patch.r * 0.7 * np.sin(ang * np.pi / 180)
        if (patch.theta2 - patch.theta1) < 5.:
            txt.set_position((x, y))
   
#Set plot annotations
ax1.text(sum(fauthors)/len(fauthors)-1.5, 38, 'Average female authorship', 
         rotation=90, color=cold[1], **afont)
ax3.text(sum(mauthors)/len(mauthors)-1.5, 39.5, 'Average male authorship', 
         rotation=90, color=warm[-1], **afont)
    
#Set figure titles
fig1.text(0.5,0.970,'% female authorship in organisation-led papers', 
          horizontalalignment='center', verticalalignment='top', **hfont)
fig1.text(0.5,0.470,'% male authorship in organisation-led papers', 
          horizontalalignment='center', verticalalignment='top', **hfont)

#Configure plot boxes
rect1 = plt.Rectangle((0.02, 0.02), 0.95, 0.97, fill=False, color='#767676', 
                      lw=1, zorder=1000, transform=fig1.transFigure, 
                      figure=fig1)
fig1.patches.extend([rect1])

#Plot and save
plt.savefig('output/authorship_genders.jpg', dpi=300)
# plt.show()
plt.close()


#------------   Gender % when 1st/last author is male or female   -------------


#Set font styles and colour palettes
hfont = {'fontname':'Arial', 'fontsize':16}#, 'fontweight': 'bold'}
lfont1 = {'fontname':'Arial', 'fontsize':13}  
lfont2 = {'fontname':'Arial', 'fontsize':13, 'color':'#5D5D5D'} 
tfont = {'fontname':'Arial', 'fontsize':12, 'color':'#5D5D5D'}

#Prime plots
fig1, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)) = plt.subplots(4, 2, 
                                                              figsize=(10,10),
                                                              gridspec_kw={'wspace':0, 
                                                                           'hspace':0},
                                                              sharex=True,
                                                              sharey=True)

#Iterate through plots
for i,ax,t,c1,c2 in zip([['first_gender','female'], ['first_gender','male'],
                        ['last_gender','female'], ['last_gender','male']],
                        [[ax1,ax2],[ax3,ax4],[ax5,ax6],[ax7,ax8]], 
                        ['Female lead author', 'Male lead author', 
                        'Female last author', 'Male last author'],
                        cold[1:6], reversed(warm[1:6])):
    
    #Compute gender percentages from female/male-led authorships
    gens = df.loc[df[i[0]]==i[1]] 
    
    #Get gender distribution bins
    fauthors, mauthors, nbauthors = getGenderDistrib(gens, first=False)
    h1,e1 = np.histogram(fauthors, bins=bin10)
    h2,e2 = np.histogram(mauthors, bins=bin10)
    
    #Plot as bar histograms
    ax[0].bar(list(range(0, (len(bin10)-1)*10, 10)), h1, width=10, color=c1, 
              edgecolor='white')
    ax[1].bar(list(range(0, (len(bin10)-1)*10, 10)), h2, width=10, color=c2, 
              edgecolor='white')
       
    #Twin y axes
    twinax = ax[1].twinx()
    twinax.set_ylim(0,180)
    twinax.set_yticks([0,30,60,90,120,150,180])
    twinax.set_yticklabels(['0', '', '60','', '120', '', ''], tfont)  
    
#Set ticks and grids for all plots
for ax in [ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8]:  
    ax.set_axisbelow(True)
    ax.grid(color='gray', linestyle='dashed', axis='y') 
    ax.set_xlim(-5, ((len(bin10)-1)*10)-5)
    ax.set_xticks([0,10,20,30,40,50,60,70,80,90,100,110])
    ax.set_xticklabels(l10, tfont, rotation=45)
    ax.set_ylim(0,180)
    ax.set_yticks([0,30,60,90,120,150,180])
    ax.set_yticklabels(['0', '', '60','', '120', '', ''], tfont)  

#Set labels
ax7.set_ylabel('Number of publications', **lfont2)
twinax.set_ylabel('Number of publications', **lfont2, rotation=270)
ax7.yaxis.set_label_coords(-0.1, 2)
twinax.yaxis.set_label_coords(1.15, 2)
ax7.set_xlabel('% female co-authorship', labelpad=10, **lfont1)
ax8.set_xlabel('% male co-authorship', labelpad=10, **lfont1)

#Set plot titles
posx=0.51
posy=0.84
for txt in ['Female lead author', 'Male lead author', 
            'Female last author', 'Male last author']:
    fig1.text(posx, posy, txt, ha='center', 
              bbox=dict(lw=1, ec='k', facecolor='w', boxstyle='round', 
              alpha=1), transform=fig1.transFigure, **lfont1)
    posy=posy-0.193
fig1.text(0.51, 0.96, 
          'Co-authorship gender composition based on first and last author gender', 
          ha='center', **hfont)

#Set twin x axes
for ax in [ax1,ax2]:
    twinax = ax.twiny()
    twinax.set_xlim(-5, ((len(bin10)-1)*10)-5)
    twinax.set_xticks([0,10,20,30,40,50,60,70,80,90,100,110])
    twinax.set_xticklabels(l10, tfont, rotation=45)

#Plot and save
plt.rcParams["font.family"] = fontname
plt.savefig('output/authorship_lead_last.jpg', dpi=300)
# plt.show()
plt.close()
     

#------------------------------------------------------------------------------

print('Finished')
