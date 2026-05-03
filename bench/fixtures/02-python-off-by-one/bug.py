def paginate(items, page, per_page):
    start = page * per_page
    end = start + per_page
    return items[start:end]


def get_page(items, page, per_page):
    last_page = len(items) // per_page
    if page > last_page:
        raise ValueError(f"page {page} out of range (max {last_page})")
    return paginate(items, page, per_page)


if __name__ == "__main__":
    items = list(range(10))
    print(get_page(items, 2, 5))
