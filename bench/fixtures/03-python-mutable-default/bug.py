def add_event(name, log=[]):
    log.append(name)
    return log


def session_events(events):
    result = []
    for e in events:
        result = add_event(e)
    return result


if __name__ == "__main__":
    print(session_events(["a", "b"]))
    print(session_events(["c", "d"]))
