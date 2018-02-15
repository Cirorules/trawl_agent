import requests


def httpd_stats(url, user=None, password=None):
    try:
        req = requests.get(url)
    except Exception as e:
        print(str(e))
        raise

    stats = {}
    for line in req.text.split('\n'):
        line = line.split(':')
        if len(line) == 2:
            stat, value = line
            try:
                value = float(value)
                stats[stat] = value
            except ValueError:
                continue

    return stats