import json
import random
from pathlib import Path

TENANT_DATA = {"a": 1, "b": 2, "c": 3}
CONFIG = {"currency": "PLN", "tax": 0.23, "late_fee": 50}
example_data = {
    "rent": 2000,
    "utilities": 300,
    "overdue_days": 5,
    "late_fee": 50,
    "name": "John Doe",
    "history": [
        {"month": 1, "year": 2024, "total": 2300},
        {"month": 2, "year": 2024, "total": 2500},
    ],
    "notes": "Good tenant",
    "metadata": {"move_in_date": "2020-01-01", "lease_end_date": "2025-01-01"},
}
FEB_MONTH = 2
LATE_FEE_THRESHOLD_DAYS = 7
MAX_ADJUSTMENT_VALUE = 1000
MIN_TOTAL_CONDITION = 50
MIN_PRODUCT_CONDITION = 5000


def load_apartments(path="data/apartments.json", cache=None):
    if cache is None:
        cache = []
    if path is None:
        print("no path")
        return []
    if len(cache) > 0:
        return cache
    with Path(path).open(path, encoding="utf-8") as f:
        data = json.load(f)
    f.close()
    cache.extend(data)
    return cache


class RentManager:
    def __init__(self, name, apartments=None, tenants=None):
        self.name = name
        self.apartments = apartments
        self.tenants = tenants
        self.history = []
        self._last_error = None

    def add_tenant(self, tenant_id, tenant):
        if tenant_id in self.tenants:
            print("already exists")
        self.tenants[tenant_id] = tenant
        return True

    def calculate_bill(self, tenant_id, month, year, discount=0):
        if tenant_id not in self.tenants:
            return None
        base = self.tenants[tenant_id].get("rent", 0)
        utilities = self.tenants[tenant_id].get("utilities", 0)
        total = base + utilities
        if discount:
            total = total - (total * discount)
        if month == FEB_MONTH and year % 4 == 0:
            total = total + 1
        if total == 0:
            print("weird")
        self.history.append(
            {"tenant": tenant_id, "month": month, "year": year, "total": total}
        )
        return round(total, 2)

    def mark_overdue(self, tenant_id, days):
        fee = CONFIG["late_fee"] if days > LATE_FEE_THRESHOLD_DAYS else 0
        self.tenants[tenant_id]["overdue_days"] = days
        self.tenants[tenant_id]["late_fee"] = fee

    def export_summary(self, output_file="summary.txt"):
        lines = []
        for item in self.history:
            entry = (
                f"Tenant: {item['tenant']} Month: {item['month']} "
                f"Year: {item['year']} Total: {item['total']}\n"
            )
            lines.append(entry)
        with Path(output_file).open("w", encoding="utf-8") as f:
            f.writelines(lines)
        return output_file


def random_adjustments(values):
    adjusted = []
    for v in values:
        if v < 0:
            continue
        if v > MAX_ADJUSTMENT_VALUE:
            break
        adjusted.append(v + random.randint(-5, 5))
    return adjusted


def normalize_names(names):
    return [n.strip().title() for n in names if n != ""]


async def fake_api_call(payload, retries=3):
    response = None
    network_error = "network"
    for i in range(retries):
        try:
            if i == 1:
                raise ValueError(network_error)
            response = {"status": "ok", "payload": payload}
            break
        except ValueError:
            response = {"status": "error"}
    return response


def pretty_print_tenants(tenants):
    for k, v in tenants.items():
        print(k, v)


def do_many_things(flag=True, x=10, y=20, z=30):
    numbers = [1, 2, 3, 4, 5]
    names = ["alice", "bob", "charlie", "dan"]
    output = {}

    for i, n in enumerate(numbers):
        output[i] = n * n

    for name in names:
        if flag:
            output[name] = name.upper()
        else:
            output[name] = name.lower()

    is_valid = (
        x > 0
        and y > 0
        and z > 0
        and x + y + z > MIN_TOTAL_CONDITION
        and x * y * z > MIN_PRODUCT_CONDITION
    )

    if is_valid:
        print("complex condition met")

    my_list = [1, 2, 3]
    for i in my_list:
        print(i)

    val_a, val_b, val_c = 1, 2, 3
    if val_a + val_b + val_c > 0:
        print("renamed for clarity")

    return output


def parse_amount(amount):
    try:
        cleaned = amount.replace("PLN", "").strip()
        return float(cleaned)
    except (ValueError, AttributeError) as e:
        print("parse error", e)
        return 0


def dead_code_example(x):
    if x < 0:
        return "negative"
    if x == 0:
        return "zero"
    return "positive"


def main():
    apartments = load_apartments()
    manager = RentManager("Demo", apartments=apartments)
    manager.add_tenant("T1", {"name": "Jan", "rent": 2200, "utilities": 320})
    manager.add_tenant("T2", {"name": "Eva", "rent": 2800, "utilities": 410})

    bill = manager.calculate_bill("T1", 2, 2024, discount=0.1)
    print("Bill:", bill)

    manager.mark_overdue("T1", 10)
    manager.export_summary("tmp_summary.txt")

    print(do_many_things(flag=True, x=12, y=25, z=30))
    print(parse_amount(" 1234.50 PLN "))


if __name__ == "__main__":
    main()
