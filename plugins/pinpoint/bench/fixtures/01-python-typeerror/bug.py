PROMOS = {"SAVE10": 0.10, "SAVE20": 0.20}


def apply_discount(promo_code, price):
    return price * (1 - PROMOS[promo_code])


def line_total(item):
    base = item["price"] * item["qty"]
    return apply_discount(item["promo"], base)


def cart_total(items):
    return sum(line_total(i) for i in items)


if __name__ == "__main__":
    cart = [
        {"price": 10, "qty": 2, "promo": "SAVE10"},
        {"price": 5, "qty": 1},
    ]
    print(cart_total(cart))
