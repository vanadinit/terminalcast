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
