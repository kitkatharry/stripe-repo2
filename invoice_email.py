"""
Create a Stripe invoice and email it to a recipient.

Usage:
    export STRIPE_SECRET_KEY=sk_test_...
    python invoice_email.py --email harry@castlefamily.co.uk --amount 0.30

The script will:
  1. Create (or reuse) a customer identified by email.
  2. Add a one-time invoice item in the smallest currency unit (e.g., pence).
  3. Create an invoice set to be sent via email.
  4. Finalize and send the invoice.

Requires the `stripe` Python package: pip install stripe
"""

import argparse
import os
import sys
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

import stripe


DEFAULT_EMAIL = "harry@castlefamily.co.uk"
DEFAULT_AMOUNT_MAJOR = Decimal("0.30")
DEFAULT_CURRENCY = "gbp"
DEFAULT_DESCRIPTION = "One-time charge"


def get_stripe_api_key() -> str:
    api_key = os.environ.get("STRIPE_SECRET_KEY")
    if not api_key:
        raise RuntimeError("Set STRIPE_SECRET_KEY environment variable with your Stripe secret key")
    return api_key


def find_or_create_customer(email: str, name: Optional[str] = None) -> stripe.Customer:
    existing_customers = stripe.Customer.search(query=f"email:'{email}'", limit=1)
    if existing_customers.data:
        return existing_customers.data[0]
    return stripe.Customer.create(email=email, name=name)


def create_invoice_item(customer_id: str, amount_minor: int, currency: str, description: Optional[str] = None) -> stripe.InvoiceItem:
    return stripe.InvoiceItem.create(
        customer=customer_id,
        amount=amount_minor,
        currency=currency,
        description=description,
    )


def create_and_send_invoice(customer_id: str) -> stripe.Invoice:
    invoice = stripe.Invoice.create(
        customer=customer_id,
        collection_method="send_invoice",
        days_until_due=30,
        auto_advance=False,
    )

    finalized = stripe.Invoice.finalize_invoice(invoice.id)
    stripe.Invoice.send_invoice(finalized.id)
    return finalized


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create and email a Stripe invoice")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="Recipient email address")
    parser.add_argument(
        "--name",
        default=None,
        help="Optional customer name to associate with the invoice",
    )
    parser.add_argument(
        "--amount",
        type=Decimal,
        default=DEFAULT_AMOUNT_MAJOR,
        help="Invoice amount in major units (e.g., pounds).",
    )
    parser.add_argument(
        "--currency",
        default=DEFAULT_CURRENCY,
        help="Currency code (e.g., gbp).",
    )
    parser.add_argument(
        "--description",
        default=DEFAULT_DESCRIPTION,
        help="Description for the invoice item.",
    )
    return parser.parse_args(argv)


def convert_major_to_minor(amount_major: Decimal) -> int:
    minor = (amount_major * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if minor <= 0:
        raise ValueError("Amount must be greater than zero")
    return int(minor)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or [])
    stripe.api_key = get_stripe_api_key()

    amount_minor = convert_major_to_minor(args.amount)
    customer = find_or_create_customer(args.email, args.name)
    create_invoice_item(customer.id, amount_minor, args.currency, args.description)
    invoice = create_and_send_invoice(customer.id)

    print(
        f"Created and sent invoice {invoice.id} to {args.email} for {args.amount} {args.currency.upper()}"
    )


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as exc:  # pragma: no cover - simple script guard
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
