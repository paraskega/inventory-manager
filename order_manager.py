"""
Order & Inventory Management System
Silver - Ξενοδοχειακός Εξοπλισμός
Georgios Paraskeva, 2025
"""

import csv
import os
from datetime import datetime


# ── Δεδομένα (σε πραγματική χρήση διαβάζονται από CSV) ──────────────────────

SAMPLE_INVENTORY = [
    {"code": "PRD-001", "name": "Κάδος Ξενοδοχείου 30L", "category": "Δοχεία", "qty": 45, "min_qty": 20},
    {"code": "PRD-002", "name": "Σαπουνοθήκη Τοίχου",    "category": "Αξεσουάρ", "qty": 8,  "min_qty": 15},
    {"code": "PRD-003", "name": "Κρεμάστρα Μπάνιου",      "category": "Αξεσουάρ", "qty": 60, "min_qty": 25},
    {"code": "PRD-004", "name": "Καλάθι Απορριμμάτων 5L", "category": "Δοχεία",   "qty": 12, "min_qty": 30},
    {"code": "PRD-005", "name": "Ραφιέρα Μπάνιου",        "category": "Έπιπλα",   "qty": 3,  "min_qty": 10},
]

SAMPLE_ORDERS = [
    {"order_id": "ORD-2025-001", "client": "Ξενοδοχείο Μακεδονία",  "product_code": "PRD-001", "qty": 20, "status": "Εκκρεμεί",      "order_date": "2025-09-01", "delivery_date": "2025-09-10"},
    {"order_id": "ORD-2025-002", "client": "Boutique Hotel Egnatia", "product_code": "PRD-003", "qty": 40, "status": "Σε Εξέλιξη",    "order_date": "2025-09-03", "delivery_date": "2025-09-12"},
    {"order_id": "ORD-2025-003", "client": "Ξενοδοχείο Μακεδονία",  "product_code": "PRD-002", "qty": 15, "status": "Παραδόθηκε",    "order_date": "2025-08-20", "delivery_date": "2025-08-28"},
    {"order_id": "ORD-2025-004", "client": "City Hotel Thessaloniki","product_code": "PRD-004", "qty": 25, "status": "Εκκρεμεί",      "order_date": "2025-09-05", "delivery_date": "2025-09-15"},
    {"order_id": "ORD-2025-005", "client": "Boutique Hotel Egnatia", "product_code": "PRD-005", "qty": 8,  "status": "Εκκρεμεί",      "order_date": "2025-09-06", "delivery_date": "2025-09-18"},
]


# ── Βασικές λειτουργίες ──────────────────────────────────────────────────────

def check_inventory(inventory):
    """Επιστρέφει λίστα με προϊόντα που χρειάζονται αναπλήρωση."""
    return [item for item in inventory if item["qty"] < item["min_qty"]]


def get_orders_by_status(orders, status):
    """Φιλτράρει παραγγελίες βάσει κατάστασης."""
    return [o for o in orders if o["status"] == status]


def get_orders_by_client(orders, client_name):
    """Επιστρέφει όλες τις παραγγελίες ενός πελάτη."""
    return [o for o in orders if client_name.lower() in o["client"].lower()]


def calculate_inventory_after_orders(inventory, orders):
    """
    Υπολογίζει το προβλεπόμενο απόθεμα αφαιρώντας
    τις εκκρεμείς και σε εξέλιξη παραγγελίες.
    """
    active_statuses = {"Εκκρεμεί", "Σε Εξέλιξη"}
    consumption = {}
    for o in orders:
        if o["status"] in active_statuses:
            consumption[o["product_code"]] = consumption.get(o["product_code"], 0) + o["qty"]

    projected = []
    for item in inventory:
        reserved = consumption.get(item["code"], 0)
        projected_qty = item["qty"] - reserved
        projected.append({**item, "reserved": reserved, "projected_qty": projected_qty})
    return projected


def export_report_csv(data, filename, fieldnames):
    """Εξάγει δεδομένα σε CSV αρχείο."""
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
    print(f"  → Αρχείο αποθηκεύτηκε: {filename}")


# ── Εκτύπωση αναφορών ────────────────────────────────────────────────────────

def print_separator(char="─", width=60):
    print(char * width)


def print_header(title):
    print_separator("═")
    print(f"  {title}")
    print_separator("═")


def report_inventory_status(inventory):
    print_header("ΚΑΤΑΣΤΑΣΗ ΑΠΟΘΕΜΑΤΩΝ")
    low_stock = check_inventory(inventory)

    for item in inventory:
        status = "⚠️  ΑΝΑΠΛΗΡΩΣΗ" if item["qty"] < item["min_qty"] else "✅ ΟΚ"
        print(f"  {item['code']}  {item['name']:<30}  Απόθεμα: {item['qty']:>4}  Ελάχιστο: {item['min_qty']:>4}  {status}")

    print_separator()
    if low_stock:
        print(f"\n  ⚠️  {len(low_stock)} προϊόν(τα) χρειάζονται άμεση αναπλήρωση:")
        for item in low_stock:
            shortage = item["min_qty"] - item["qty"]
            print(f"     • {item['name']} (έλλειμμα: {shortage} τεμ.)")
    else:
        print("\n  ✅ Όλα τα αποθέματα είναι επαρκή.")
    print()


def report_orders_summary(orders):
    print_header("ΣΥΝΟΨΗ ΠΑΡΑΓΓΕΛΙΩΝ")
    statuses = ["Εκκρεμεί", "Σε Εξέλιξη", "Παραδόθηκε"]
    for s in statuses:
        count = len(get_orders_by_status(orders, s))
        bar = "█" * count
        print(f"  {s:<15} {bar} ({count})")
    print()

    pending = get_orders_by_status(orders, "Εκκρεμεί")
    if pending:
        print("  Εκκρεμείς παραγγελίες:")
        print_separator()
        for o in pending:
            print(f"  {o['order_id']}  Πελάτης: {o['client']:<30}  Παράδοση: {o['delivery_date']}")
    print()


def report_projected_inventory(inventory, orders):
    print_header("ΠΡΟΒΛΕΠΟΜΕΝΟ ΑΠΟΘΕΜΑ (μετά από εκκρεμείς παραγγελίες)")
    projected = calculate_inventory_after_orders(inventory, orders)
    warnings = 0
    for item in projected:
        status = "⚠️  ΚΡΙΤΙΚΟ" if item["projected_qty"] < item["min_qty"] else "✅ ΟΚ"
        if item["projected_qty"] < item["min_qty"]:
            warnings += 1
        print(f"  {item['code']}  {item['name']:<30}  Τώρα: {item['qty']:>4}  Δεσμευμένο: {item['reserved']:>4}  Πρόβλεψη: {item['projected_qty']:>4}  {status}")
    print_separator()
    print(f"\n  Σύνολο κρίσιμων αποθεμάτων μετά παραγγελίες: {warnings}")
    print()
    return projected


# ── Κύριο πρόγραμμα ──────────────────────────────────────────────────────────

def main():
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    print(f"\n  Silver — Σύστημα Διαχείρισης Παραγγελιών & Αποθεμάτων")
    print(f"  Αναφορά: {now}\n")

    report_inventory_status(SAMPLE_INVENTORY)
    report_orders_summary(SAMPLE_ORDERS)
    projected = report_projected_inventory(SAMPLE_INVENTORY, SAMPLE_ORDERS)

    # Εξαγωγή CSV αναφορών
    print_header("ΕΞΑΓΩΓΗ ΑΡΧΕΙΩΝ")
    export_report_csv(
        projected,
        "report_inventory.csv",
        ["code", "name", "category", "qty", "reserved", "projected_qty", "min_qty"]
    )
    export_report_csv(
        SAMPLE_ORDERS,
        "report_orders.csv",
        ["order_id", "client", "product_code", "qty", "status", "order_date", "delivery_date"]
    )
    print("\n  ✅ Ολοκληρώθηκε.\n")


if __name__ == "__main__":
    main()
