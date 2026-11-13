"""Statistics lab: python run_tests.py --family all [--alpha 0.05]
Run offline using CSVs from data/. Saves results.csv and visualization PNGs.
"""
import argparse
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.stats.proportion import proportions_ztest
from statsmodels.tsa.stattools import adfuller, kpss, acf
from statsmodels.stats.diagnostic import acorr_ljungbox
import statsmodels.formula.api as smf

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; OUTPUT=ROOT/'outputs'; OUTPUT.mkdir(exist_ok=True)
CLIENTS=pd.read_csv(DATA/'clients.csv'); O=pd.read_csv(DATA/'orders.csv'); S=pd.read_csv(DATA/'strategies.csv'); M=pd.read_csv(DATA/'market_daily.csv'); P=pd.read_csv(DATA/'rare_product_pilot.csv')
records=[]

def record(family,name,null,statistic,p,interpret='',alpha=.05):
 p=float(p)
 records.append(dict(family=family,test=name,null_hypothesis=null,statistic=round(float(statistic),6),p_value=round(p,8),decision=('Reject H0' if p<alpha else 'Fail to reject H0'),business_context=interpret))
 print(f'{family:15s} | {name:32s} | p={p:.5g} | {records[-1]["decision"]}')

def fig_save(name):
 plt.tight_layout(); plt.savefig(OUTPUT/f'{name}.png',dpi=145);plt.close()

def means(alpha):
 f='means'
 x=S.loc[S.strategy=='Balanced','monthly_return']; y=S.loc[S.strategy=='Growth','monthly_return']
 t=stats.ttest_1samp(x,0);record(f,'One-sample t','Balanced mean return = 0',*t,'Test strategy returns vs zero',alpha)
 t=stats.ttest_ind(x,y,equal_var=False);record(f,'Welch two-sample t','Balanced mean = Growth mean',*t,'Compare independent strategy return samples',alpha)
 d=CLIENTS.latency_after_ms-CLIENTS.latency_before_ms
 t=stats.ttest_rel(CLIENTS.latency_after_ms,CLIENTS.latency_before_ms);record(f,'Paired t','Mean before-after latency change = 0',*t,'Same clients measured twice',alpha)
 groups=[g.monthly_return.values for _,g in S.groupby('strategy')]
 t=stats.f_oneway(*groups);record(f,'One-way ANOVA','All strategy mean returns equal',*t,'Compare four strategy returns',alpha)
 # Z test with stated (hypothetically known) population standard deviation.
 known_sigma=.026; z=(x.mean()-0)/(known_sigma/np.sqrt(len(x)))
 record(f,'One-sample z (known sigma)','Balanced mean return = 0',z,2*stats.norm.sf(abs(z)),'Pedagogical only: sigma assumed KNOWN',alpha)
 plt.figure(figsize=(9,5));S.boxplot(column='monthly_return',by='strategy',grid=False);plt.suptitle('');plt.title('Monthly returns across strategies');plt.ylabel('Return (fraction)');fig_save('means_strategy_boxplot')
 plt.figure(figsize=(8,4));plt.hist(d,bins=35);plt.axvline(0,color='black',linestyle='--');plt.title('Paired change: latency after minus before');plt.xlabel('Milliseconds');fig_save('means_paired_latency')

def variance(alpha):
 f='variance'; x=S[S.strategy=='Balanced'].monthly_return; y=S[S.strategy=='Momentum'].monthly_return
 s1=x.var(ddof=1);s2=y.var(ddof=1);F=s1/s2;df1=len(x)-1;df2=len(y)-1;p=2*min(stats.f.cdf(F,df1,df2),stats.f.sf(F,df1,df2))
 record(f,'Classical F variance','Variance Balanced = Momentum',F,min(p,1),'Requires independent normal samples',alpha)
 for name,func in [('Levene median',lambda:stats.levene(x,y,center='median')),('Bartlett',lambda:stats.bartlett(x,y))]:
  result=func();record(f,name,'Variances equal',*result,'Bartlett sensitive to non-normality',alpha)
 plt.figure(figsize=(8,4));plt.hist(x,bins=28,alpha=.6,label='Balanced');plt.hist(y,bins=28,alpha=.6,label='Momentum');plt.legend();plt.title('Same location? Different dispersion of returns');fig_save('variance_returns')

def proportions(alpha):
 f='proportions'; gb=CLIENTS.groupby('experiment_arm')['onboarded'].agg(['sum','count']); a=gb.loc['Control']; b=gb.loc['New App']
 t=proportions_ztest([a['sum'],b['sum']],[a['count'],b['count']]);record(f,'Two proportion z','Conversion rates equal',*t,'Randomized experiment arms; compare rates',alpha)
 t=proportions_ztest(CLIENTS.onboarded.sum(),len(CLIENTS),value=.30);record(f,'One proportion z','Overall conversion rate = 30%',*t,'Benchmark test; reference rate assumed',alpha)
 observed=O.asset_class.value_counts().reindex(['Equities','ETFs','Mutual Funds','Options']).values
 t=stats.chisquare(observed,f_exp=len(O)*np.array([.40,.30,.20,.10]));record(f,'Chi-square goodness of fit','Asset mix is 40/30/20/10 percent',*t,'Compare observed trade mix to policy mix',alpha)
 rates=gb['sum']/gb['count'];plt.figure(figsize=(6,4));rates.plot.bar();plt.title('Onboarding conversion by experiment arm');plt.ylabel('Conversion rate');plt.ylim(0,.6);fig_save('proportions_conversion')

def association(alpha):
 f='association'; tab=pd.crosstab(CLIENTS.risk_profile,CLIENTS.advisory_adopted)
 t=stats.chi2_contingency(tab,correction=False);record(f,'Chi-square independence','Risk profile and advisory adoption independent',t.statistic,t.pvalue,'Categorical association; not causation',alpha)
 small=pd.crosstab(P['product'],P.complaint).reindex(index=['ETF','Structured Note'],columns=[0,1],fill_value=0)
 t=stats.fisher_exact(small.to_numpy());record(f,'Fisher exact','Complaint probability independent of product',*t,'Small counts; odds ratio is the statistic',alpha)
 tab.div(tab.sum(axis=1),axis=0).plot.bar(stacked=True,figsize=(7,4));plt.title('Advisory adoption fraction within risk group');plt.ylabel('Share');fig_save('association_risk_advisory')

def correlation(alpha):
 f='correlation';x=CLIENTS.digital_score;y=CLIENTS.monthly_trades
 for name,fn in [('Pearson',stats.pearsonr),('Spearman',stats.spearmanr),('Kendall tau',stats.kendalltau)]:
  t=fn(x,y);record(f,name,'No corresponding linear/rank association',t.statistic,t.pvalue,'Digital engagement vs activity; not causality',alpha)
 plt.figure(figsize=(8,5));plt.scatter(x,y,s=6,alpha=.22);plt.title('Digital score and monthly trades');plt.xlabel('Digital score');plt.ylabel('Number of trades');fig_save('correlation_digital_trades')

def regression(alpha):
 f='regression';model=smf.ols('monthly_revenue_usd ~ digital_score + C(segment) + monthly_trades',data=CLIENTS).fit(cov_type='HC3')
 for term in ['digital_score','monthly_trades']:
  record(f,'Robust coefficient t: '+term,'Coefficient = 0',model.tvalues[term],model.pvalues[term],'HC3 heteroskedasticity-robust SE; association not causality',alpha)
 # Overall regression significance from non-robust conventional F test (model fitted with robust covariance has a robust Wald F).
 record(f,'Overall model F','All non-intercept coefficients = 0',model.fvalue,model.f_pvalue,'Joint significance with HC3 robust covariance',alpha)
 plt.figure(figsize=(8,5));plt.scatter(model.fittedvalues,model.resid,s=7,alpha=.25);plt.axhline(0,color='black',linestyle='--');plt.xlabel('Predicted revenue');plt.ylabel('Residual');plt.title('OLS residuals vs predictions');fig_save('regression_residuals')
 (OUTPUT/'regression_summary.txt').write_text(str(model.summary()),encoding='utf-8')

def nonparametric(alpha):
 f='nonparametric'; d=CLIENTS.latency_after_ms-CLIENTS.latency_before_ms
 t=stats.wilcoxon(d);record(f,'Wilcoxon signed-rank','Paired differences symmetric about zero',*t,'Ranked paired latency differences; symmetry assumption',alpha)
 a=O[O.engine=='Legacy'].execution_latency_ms; b=O[O.engine=='Optimized'].execution_latency_ms
 t=stats.mannwhitneyu(a,b,alternative='two-sided');record(f,'Mann-Whitney U','Group rank distributions same',*t,'Latency distribution across independent engines',alpha)
 groups=[g.monthly_return.values for _,g in S.groupby('strategy')]
 t=stats.kruskal(*groups);record(f,'Kruskal-Wallis','Strategy rank distributions same',*t,'Multiple groups; not automatically a median test',alpha)
 plt.figure(figsize=(8,4));O.boxplot(column='execution_latency_ms',by='engine',grid=False,showfliers=False);plt.suptitle('');plt.title('Execution latency by engine (outliers hidden)');plt.ylabel('Milliseconds');fig_save('nonparametric_order_latency')

def distribution(alpha):
 f='distribution';x=M.daily_return.values
 z=(x-x.mean())/x.std(ddof=1)
 # Lilliefors is preferable to naive KS when mu/sigma fitted; here KS is against a fully specified N(0,1) for teaching, but parameters estimated invalidates nominal p-value.
 from statsmodels.stats.diagnostic import lilliefors
 t=lilliefors(x,dist='norm');record(f,'Lilliefors normality','Returns are normal with fitted mean/variance',t[0],t[1],'Corrected KS-type test for estimated normal parameters',alpha)
 t=stats.jarque_bera(x);record(f,'Jarque-Bera','Normal skew and kurtosis',t.statistic,t.pvalue,'Heavy tails or skew invalidate normality',alpha)
 t=stats.anderson(x,dist='norm'); # significance 5% threshold may be interpolated? report critical value comparison not p.
 ix=np.argmin(abs(np.asarray(t.significance_level)-5))
 print(f'distribution    | Anderson-Darling normality     | statistic={t.statistic:.4f}, {t.significance_level[ix]}% critical={t.critical_values[ix]:.4f} (no p-value)')
 records.append(dict(family=f,test='Anderson-Darling',null_hypothesis='Returns follow a normal distribution',statistic=round(float(t.statistic),6),p_value=np.nan,decision=('Reject H0 at 5%' if t.statistic>t.critical_values[ix] else 'Fail to reject H0 at 5%'),business_context='Critical-value inference, not a p-value'))
 # Valid one-sample KS illustration with fully specified reference, without estimating its parameters.
 t=stats.kstest(x,'norm',args=(0,.01));record(f,'KS specified N(0,0.01)','Returns have fully specified N(0, .01) distribution',*t,'Reference mean/std specified externally, not estimated from x',alpha)
 fig,axes=plt.subplots(1,2,figsize=(10,4));axes[0].hist(x,bins=45,density=True);xx=np.linspace(x.min(),x.max(),300);axes[0].plot(xx,stats.norm.pdf(xx,loc=x.mean(),scale=x.std(ddof=1)));axes[0].set_title('Returns vs fitted normal curve');stats.probplot(x,dist='norm',plot=axes[1]);axes[1].set_title('Normal Q-Q plot');fig_save('distribution_normality')

def timeseries(alpha):
 f='timeseries';price=M.price_index.values;returns=M.daily_return.values
 for label,x in [('price index',price),('daily returns',returns)]:
  with warnings.catch_warnings():
   warnings.simplefilter('ignore')
   t=adfuller(x,autolag='AIC');record(f,'ADF '+label,'Unit root present',t[0],t[1],'Rejection supports no unit root under chosen deterministic terms',alpha)
   t=kpss(x,regression='c',nlags='auto');record(f,'KPSS '+label,'Level stationary',t[0],t[1],'p-value often bounded; complement to ADF',alpha)
 lb=acorr_ljungbox(returns,lags=[5,10,20],return_df=True)
 for lag,row in lb.iterrows(): record(f,f'Ljung-Box returns lag {lag}','No autocorrelation up to this lag',row.lb_stat,row.lb_pvalue,'Multiple lags inspected; account for multiplicity',alpha)
 fig,axes=plt.subplots(2,1,figsize=(10,6));axes[0].plot(pd.to_datetime(M.date),price);axes[0].set_title('Synthetic price index');axes[1].plot(pd.to_datetime(M.date),returns);axes[1].set_title('Daily returns');fig_save('timeseries_prices_returns')
 fig,ax=plt.subplots(figsize=(7,4));ax.bar(range(1,21),acf(returns,nlags=20,fft=True)[1:]);ax.axhline(0,color='black');ax.set_title('ACF of daily returns');ax.set_xlabel('Lag');fig_save('timeseries_autocorrelation')

FAMILIES=dict(means=means,variance=variance,proportions=proportions,association=association,correlation=correlation,regression=regression,nonparametric=nonparametric,distribution=distribution,timeseries=timeseries)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--family',choices=['all',*FAMILIES],default='all');parser.add_argument('--alpha',type=float,default=.05);args=parser.parse_args()
 for name,func in FAMILIES.items():
  if args.family in ('all',name):func(args.alpha)
 df=pd.DataFrame(records);df.to_csv(OUTPUT/'results.csv',index=False)
 print(f'\nSaved {len(df)} test rows to {OUTPUT/"results.csv"} and plots to {OUTPUT}')
 print('CAUTION: p < alpha is evidence against H0, not proof of causality or business impact.')
if __name__=='__main__':main()
