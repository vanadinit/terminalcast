from typing import List


def selector(entries: List[tuple]):
    """Provides a command line interface for selecting from multiple entries
    :param entries: List of Tuples(entry: Any, label: str)
    """
    match len(entries):
        case 0:
            return None
        case 1:
            return entries[0][0]
        case _:
            entry_labels = '\n'.join([
                f'{index}: {entry[1]}'
                for index, entry in enumerate(entries)
            ])
            try:
                return entries[int(input(f'Found multiple entries, please choose: \n{entry_labels}\n'))][0]
            except (ValueError, IndexError):
                print('Invalid answer! Please try again and type the number of your desired answer.')
                return selector(entries)


def format_bytes(size: int | str | None) -> str:
    if size is None:
        return "-"
    try:
        n = int(size)
    except (ValueError, TypeError):
        return "-"

    power = 1024
    if n < power:
        return f"{n} B"
    
    n_float = float(n)
    for unit in ['KB', 'MB', 'GB']:
        n_float /= power
        if n_float < power:
            return f"{n_float:.1f} {unit}"
    return f"{n_float:.1f} TB"


def simplify_user_agent(ua: str) -> str:
    if not ua or ua == '-':
        return '-'
    
    ua_lower = ua.lower()
    
    if 'crkey' in ua_lower or 'chromecast' in ua_lower:
        return 'Chromecast'
    if 'curl' in ua_lower:
        return 'Curl'
    if 'wget' in ua_lower:
        return 'Wget'
    if 'python' in ua_lower:
        return 'Python'
    
    # Browser detection
    if 'edg' in ua_lower:
        return 'Edge'
    if 'chrome' in ua_lower and 'chromium' not in ua_lower:
        return 'Chrome'
    if 'firefox' in ua_lower:
        return 'Firefox'
    if 'safari' in ua_lower and 'chrome' not in ua_lower:
        return 'Safari'
        
    # Fallback: return the first part (usually Mozilla/5.0) or a shortened version
    return ua.split(' ')[0]
