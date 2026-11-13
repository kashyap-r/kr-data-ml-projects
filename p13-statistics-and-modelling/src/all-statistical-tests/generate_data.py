"""Reproducible, fictional wealth & brokerage data. No external downloads."""
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'data'
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(20261113)
n = 2400
client_id = [f'C{i:05d}' for i in range(1,n+1)]
segment = rng.choice(['Mass Affluent','HNI','UHNI'],n,p=[.65,.28,.07])
risk = rng.choice(['Conservative','Moderate','Aggressive'],n,p=[.38,.42,.20])
digital = rng.normal(54,16,n).clip(0,100)
arm = rng.choice(['Control','New App'],n)
wealth = np.exp(rng.normal(11.3,1.0,n)) * np.select([segment=='HNI',segment=='UHNI'],[4,15],1)
base_conversion = 1/(1+np.exp(-(-1.0+.014*(digital-50)+.35*(arm=='New App'))))
onboard = rng.binomial(1,base_conversion)
advisory = rng.binomial(1,1/(1+np.exp(-(-.6 + .4*(segment=='HNI') + .85*(segment=='UHNI') + .012*(digital-50)))))
complaint = rng.binomial(1,np.clip(.065+.035*(risk=='Aggressive')-.015*(arm=='New App'),.005,.5))
revenue = rng.gamma(2.5,110,n)*(1+.6*(segment=='HNI')+2*(segment=='UHNI'))*(1+.003*digital)
activity = rng.poisson(3+.055*digital+2*(risk=='Aggressive'))
prior = np.maximum(0,rng.normal(5.3,1.4,n))
post = np.maximum(0,prior - .35 - .35*(arm=='New App')+rng.normal(0,.8,n))
clients=pd.DataFrame(dict(client_id=client_id,segment=segment,risk_profile=risk,digital_score=digital.round(2),experiment_arm=arm,wealth_usd=wealth.round(2),onboarded=onboard,advisory_adopted=advisory,complaint=complaint,monthly_revenue_usd=revenue.round(2),monthly_trades=activity,latency_before_ms=(prior*100).round(2),latency_after_ms=(post*100).round(2)))
clients.to_csv(OUT/'clients.csv',index=False)

m=5200
idx=rng.integers(0,n,m)
ci=clients.iloc[idx].reset_index(drop=True)
engine = rng.choice(['Legacy','Optimized'],m)
order_size=np.exp(rng.normal(8.2,1.3,m))
latency=np.maximum(4,rng.gamma(2.8,42,m)*(1-.27*(engine=='Optimized')))
spread=np.maximum(.01,rng.lognormal(-2.2,.65,m)*(1-.16*(engine=='Optimized')))
orders=pd.DataFrame({'order_id':[f'O{i:06d}' for i in range(m)],'client_id':ci.client_id,'risk_profile':ci.risk_profile,'engine':engine,'order_notional_usd':order_size.round(2),'execution_latency_ms':latency.round(2),'spread_bps':(spread*100).round(3),'asset_class':rng.choice(['Equities','ETFs','Mutual Funds','Options'],m,p=[.44,.30,.17,.09])})
orders.to_csv(OUT/'orders.csv',index=False)

# Independent strategy evaluation units (synthetic monthly returns); market-related time series below.
strategy=['Conservative','Balanced','Growth','Momentum']
port=[]
for s,mu,sd in zip(strategy,[.003,.006,.008,.009],[.018,.026,.043,.065]):
 for i,r in enumerate(rng.normal(mu,sd,180)):
  port.append((s,i+1,r))
pd.DataFrame(port,columns=['strategy','sample_id','monthly_return']).to_csv(OUT/'strategies.csv',index=False)

# Market-return generation: AR(1) slight persistence + volatility clusters, with matching price index.
dates=pd.bdate_range('2024-01-02',periods=360)
r=np.empty(len(dates)); vol=np.empty(len(dates));r[0]=0.;vol[0]=.009
for t in range(1,len(dates)):
 vol[t]=np.sqrt(.000012+.13*r[t-1]**2+.76*vol[t-1]**2)
 r[t]=.10*r[t-1]+rng.standard_t(7)*vol[t]/np.sqrt(7/5)
market=pd.DataFrame({'date':dates,'daily_return':r,'price_index':100*np.exp(np.cumsum(r)),'trading_volume':np.maximum(10000,rng.normal(200000,25000,len(r))*(1+9*np.abs(r)))})
market.to_csv(OUT/'market_daily.csv',index=False)

# Counts suitable for small-sample Fisher exact test, independent from the client cohort.
pd.DataFrame({'pilot_id':range(1,45),'product':['Structured Note']*22+['ETF']*22,'complaint':[1]*5+[0]*17+[1]*1+[0]*21}).to_csv(OUT/'rare_product_pilot.csv',index=False)
print('Generated:', ', '.join(f.name for f in sorted(OUT.glob('*.csv'))))
