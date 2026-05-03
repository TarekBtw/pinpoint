def add_event(name, log=[]):
    log.append(name)
    return log


def session_events(events):
    log = []
    for e in events:
        log = add_event(e, log)
    return log


if __name__ == "__main__":
    print(session_events(["a", "b"]))
    print(session_events(["c", "d"]))
