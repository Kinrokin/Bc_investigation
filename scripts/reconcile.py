#!/usr/bin/env python3
"""Exact Bartlett document arithmetic; candidate reconstructions are not recovered ledger entries."""
from __future__ import annotations
import argparse, json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
D=Decimal
CENT=D('0.01')
def money(x): return str(x.quantize(CENT,rounding=ROUND_HALF_UP))
def run():
    rows=[('2024-08-01','2025-06-30','32543.51','2711.96'),('2025-07-01','2026-06-30','33682.53','2806.28'),('2026-07-01','2027-06-30','34681.42','2905.12'),('2027-07-01','2028-06-30','36081.57','3060.80')]
    lease=[];base=D(rows[0][2]);rate=D('0.035')
    for i,(start,end,annual,monthly) in enumerate(rows):
        a,m=D(annual),D(monthly);ca=(base*(1+rate)**i).quantize(CENT,rounding=ROUND_HALF_UP);cm=(ca/12).quantize(CENT,rounding=ROUND_HALF_UP)
        lease.append(dict(start=start,end=end,printed_annual=annual,printed_monthly=monthly,monthly_times_12=money(m*12),printed_annual_minus_12_monthly=money(a-m*12),candidate_annual=money(ca),candidate_monthly=money(cm)))
    old=D('2806.88');current=D('2905.12');installments=D('4912.03');residual=old*7-installments*4
    rent=dict(status='CANDIDATE; receivable ledger not obtained',candidate_prior_monthly=money(old),candidate_prior_three_months=money(old*3),candidate_prior_five_months=money(old*5),seven_month_obligation=money(old*7),four_installments=money(installments*4),candidate_carry=money(residual),three_current_months=money(current*3),candidate_final=money(current*3+residual),reported_final='8715.40')
    intervals=[]
    for group,receipt,finance,paid in [('May-June2025','2025-08-29','2025-09-04','2025-09-12'),('July-September2025','2025-10-21','2025-12-09','2025-12-12')]:
        r,f,p=map(date.fromisoformat,(receipt,finance,paid));intervals.append(dict(group=group,receipt=receipt,finance=finance,paid=paid,receipt_to_finance=(f-r).days,finance_to_paid=(p-f).days,receipt_to_paid=(p-r).days,legal_status='Not adjudicated; request completeness/holds/governing award not resolved'))
    days=(date(2026,2,28)-date(2025,7,1)).days+1;deficit=D('426463.84')-D('380842.56')
    accounting=dict(period_days=days,revenue='380842.56',expenses='426463.84',deficit=money(deficit),daily_accounting_average=money(deficit/D(days)),cash_exhaustion_date=None,limitation='No dated cash ledger or actual September payroll/credit data')
    def path(flows):
        balance=D('10000');series=[]
        for x in flows: balance+=D(x);series.append(balance)
        return dict(final=money(balance),ever_negative=any(x<0 for x in series))
    a=path(['20000','-15000']);b=path(['-15000','20000'])
    checks=[('lease row2 difference',lease[1]['printed_annual_minus_12_monthly']=='7.17'),('lease row3 difference',lease[2]['printed_annual_minus_12_monthly']=='-180.02'),('lease row4 difference',lease[3]['printed_annual_minus_12_monthly']=='-648.03'),('candidate prior monthly',lease[1]['candidate_monthly']=='2806.88'),('candidate current monthly',lease[2]['candidate_monthly']=='2905.12'),('candidate final monthly',lease[3]['candidate_monthly']=='3006.80'),('prior check',old*3==D('8420.64')),('prior default',old*5==D('14034.40')),('four-cent carry',residual==D('0.04')),('reported arrears reproduced',current*3+residual==D('8715.40')),('14 days',intervals[0]['receipt_to_paid']==14),('52 days',intervals[1]['receipt_to_paid']==52),('49 pre-Finance days',intervals[1]['receipt_to_finance']==49),('243 accounting days',days==243),('deficit',deficit==D('45621.28')),('cash counterexample',a['final']==b['final'] and not a['ever_negative'] and b['ever_negative'])]
    failures=[n for n,ok in checks if not ok]
    if failures: raise AssertionError(failures)
    return dict(source_pages={'June22_packet':[6,12,32],'September21_statement':[2]},method='Decimal; ROUND_HALF_UP; elapsed dates except inclusive accounting period',candidate_rate=str(rate),lease_schedule=lease,rent=rent,intervals=intervals,accounting=accounting,counterexample=dict(status='ILLUSTRATION ONLY; not Bartlett transactions',receipt_first=a,payment_first=b),validation=dict(passed=len(checks),failed=0,checks=[n for n,_ in checks]),limitations=['A fitted escalation pattern is not an agreed term or actual billing proof.','The first printed lease row starts August while other term language starts July; no actual proration inferred.','No finding of hidden charges, sabotage, bank default or cash-exhaustion date.'])
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);args=parser.parse_args();payload=json.dumps(run(),indent=2)+'\n'
    if args.out: args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(payload,encoding='utf-8')
    print(payload)
