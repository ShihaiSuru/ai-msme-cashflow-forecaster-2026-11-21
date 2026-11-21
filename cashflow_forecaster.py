#!/usr/bin/env python3
"""
AI MSME Cash Flow Forecaster - Starter Demo

Practical tool for Indian MSMEs to reconcile UPI transactions with invoices
and generate short-term cash flow forecasts.

This is a self-contained starter script with sample data.
In production, integrate with bank APIs, GSTN, or Tally/Zoho exports.
"""

import csv
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict

# Sample UPI transactions (typical MSME export format)
SAMPLE_UPI = """
date,amount,description,utr
2026-11-15,45000,Payment from Sharma Traders INV-1023,UTR123456
2026-11-16,28000,UPI from Rajesh Electronics,UTR789012
2026-11-17,15000,Partial payment INV-1025,UTR345678
2026-11-18,62000,Bulk order payment,UTR901234
2026-11-19,9000,Advance for new order,UTR567890
"""

# Sample outstanding invoices
SAMPLE_INVOICES = """
invoice_id,customer,amount,due_date,status
INV-1023,Sharma Traders,45000,2026-11-14,open
INV-1024,Modern Stores,32000,2026-11-20,open
INV-1025,Rajesh Electronics,40000,2026-11-18,partial
INV-1026,City Distributors,55000,2026-11-25,open
INV-1027,Local Retail,18000,2026-11-22,open
"""

def parse_csv(data: str) -> List[Dict]:
    """Parse CSV string into list of dicts."""
    lines = data.strip().splitlines()
    reader = csv.DictReader(lines)
    return list(reader)

def reconcile_upi_with_invoices(upi_txns: List[Dict], invoices: List[Dict]) -> Dict:
    """
    Simple reconciliation: match by amount and fuzzy customer name.
    In real version, use embeddings or GSTIN matching.
    """
    matches = []
    unmatched_upi = []
    invoice_map = {inv['invoice_id']: inv for inv in invoices}
    
    for txn in upi_txns:
        matched = False
        amount = float(txn['amount'])
        desc = txn['description'].lower()
        
        for inv in invoices:
            inv_amount = float(inv['amount'])
            customer = inv['customer'].lower()
            # Simple matching logic
            if abs(amount - inv_amount) < 100 or customer in desc or inv['invoice_id'].lower() in desc:
                matches.append({
                    'upi': txn,
                    'invoice': inv,
                    'match_type': 'amount_or_name'
                })
                matched = True
                break
        
        if not matched:
            unmatched_upi.append(txn)
    
    return {'matches': matches, 'unmatched_upi': unmatched_upi}

def forecast_cashflow(reconciled: Dict, invoices: List[Dict], days: int = 30) -> Dict:
    """
    Generate simple cash flow forecast.
    - Matched payments = realized
    - Open invoices: apply collection probability based on overdue days
    """
    today = datetime(2026, 11, 21)
    forecast = {'realized': 0.0, 'expected_collections': 0.0, 'details': []}
    
    # Realized from matched UPI
    for match in reconciled['matches']:
        amt = float(match['upi']['amount'])
        forecast['realized'] += amt
        forecast['details'].append(f"Realized: ₹{amt:,.0f} from {match['invoice']['invoice_id']}")
    
    # Expected from open invoices
    for inv in invoices:
        if inv['status'] in ['open', 'partial']:
            due = datetime.strptime(inv['due_date'], '%Y-%m-%d')
            overdue_days = (today - due).days
            amount = float(inv['amount'])
            
            # Simple probability model (replace with ML in production)
            if overdue_days <= 0:
                prob = 0.85
            elif overdue_days <= 15:
                prob = 0.65
            elif overdue_days <= 30:
                prob = 0.40
            else:
                prob = 0.20
            
            expected = amount * prob
            forecast['expected_collections'] += expected
            forecast['details'].append(
                f"Expected: ₹{expected:,.0f} (₹{amount:,.0f} × {prob:.0%}) from {inv['invoice_id']} "
                f"(overdue {max(0, overdue_days)} days)"
            )
    
    total_forecast = forecast['realized'] + forecast['expected_collections']
    return {
        'horizon_days': days,
        'realized_cash': forecast['realized'],
        'expected_collections': forecast['expected_collections'],
        'total_projected': total_forecast,
        'details': forecast['details']
    }

def main():
    print("=== AI MSME Cash Flow Forecaster ===")
    print("Demo for Indian MSMEs | Date: 2026-11-21\n")
    
    upi = parse_csv(SAMPLE_UPI)
    invoices = parse_csv(SAMPLE_INVOICES)
    
    print(f"Loaded {len(upi)} UPI transactions and {len(invoices)} invoices.\n")
    
    reconciled = reconcile_upi_with_invoices(upi, invoices)
    print(f"Reconciled: {len(reconciled['matches'])} matches, "
          f"{len(reconciled['unmatched_upi'])} unmatched UPI.\n")
    
    forecast = forecast_cashflow(reconciled, invoices)
    
    print("--- 30-Day Cash Flow Forecast ---")
    print(f"Realized cash (matched UPI): ₹{forecast['realized_cash']:,.0f}")
    print(f"Expected collections (probability-weighted): ₹{forecast['expected_collections']:,.0f}")
    print(f"Total projected inflow: ₹{forecast['total_projected']:,.0f}\n")
    
    print("Breakdown:")
    for detail in forecast['details']:
        print(f"  • {detail}")
    
    print("\nNext steps for production:")
    print("  - Connect to bank UPI exports or Account Aggregator")
    print("  - Pull GST invoices via GSTN APIs")
    print("  - Train collection probability model on historical data")
    print("  - Add working capital gap alerts and GST liability tracking")

if __name__ == "__main__":
    main()
