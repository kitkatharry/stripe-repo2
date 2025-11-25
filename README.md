# Invoice Email Script

This repo contains `invoice_email.py`, a helper script to create and email an invoice via Stripe.

## Prerequisites
- Python 3.10+
- Stripe secret key with permissions to create customers and invoices
- Install dependencies: `pip install -r requirements.txt`

## Usage
1. Export your Stripe secret key:
   ```bash
   export STRIPE_SECRET_KEY=sk_test_your_key
   ```
2. Run the script with your desired options (defaults shown):
   ```bash
   python invoice_email.py \
     --email harry@castlefamily.co.uk \
     --amount 0.30 \
     --currency gbp \
     --description "One-time charge" \
     --name "Customer Name"
   ```

The script creates or reuses the customer, adds an invoice item, finalizes the invoice, and emails it to the recipient.
