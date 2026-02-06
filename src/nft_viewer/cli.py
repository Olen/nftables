"""nft-viewer CLI - iptables-like output for nftables"""

from tabulate import tabulate

import nftables
import json
import sys
import typing
import argparse

from nft_viewer import __version__


class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"
    # cancel SGR codes if we don't write to a terminal
    if not __import__("sys").stdout.isatty():
        for _ in dir():
            if isinstance(_, str) and _[0] != "_":
                locals()[_] = ""

    @staticmethod
    def Black(string: str) -> str:
        return f"{Colors.BLACK}{string}{Colors.END}"
    @staticmethod
    def Red(string: str) -> str:
        return f"{Colors.RED}{string}{Colors.END}"
    @staticmethod
    def Green(string: str) -> str:
        return f"{Colors.GREEN}{string}{Colors.END}"
    @staticmethod
    def Brown(string: str) -> str:
        return f"{Colors.BROWN}{string}{Colors.END}"
    @staticmethod
    def Blue(string: str) -> str:
        return f"{Colors.BLUE}{string}{Colors.END}"
    @staticmethod
    def Purple(string: str) -> str:
        return f"{Colors.PURPLE}{string}{Colors.END}"
    @staticmethod
    def Cyan(string: str) -> str:
        return f"{Colors.CYAN}{string}{Colors.END}"
    @staticmethod
    def LightGray(string: str) -> str:
        return f"{Colors.LIGHT_GRAY}{string}{Colors.END}"
    @staticmethod
    def DarkGray(string: str) -> str:
        return f"{Colors.DARK_GRAY}{string}{Colors.END}"
    @staticmethod
    def LightRed(string: str) -> str:
        return f"{Colors.LIGHT_RED}{string}{Colors.END}"
    @staticmethod
    def LightGreen(string: str) -> str:
        return f"{Colors.LIGHT_GREEN}{string}{Colors.END}"
    @staticmethod
    def Yellow(string: str) -> str:
        return f"{Colors.YELLOW}{string}{Colors.END}"
    @staticmethod
    def LightBlue(string: str) -> str:
        return f"{Colors.LIGHT_BLUE}{string}{Colors.END}"
    @staticmethod
    def LightPurple(string: str) -> str:
        return f"{Colors.LIGHT_PURPLE}{string}{Colors.END}"
    @staticmethod
    def LightCyan(string: str) -> str:
        return f"{Colors.LIGHT_CYAN}{string}{Colors.END}"
    @staticmethod
    def LightWhite(string: str) -> str:
        return f"{Colors.LIGHT_WHITE}{string}{Colors.END}"
    @staticmethod
    def Bold(string: str) -> str:
        return f"{Colors.BOLD}{string}{Colors.END}"
    @staticmethod
    def Underline(string: str) -> str:
        return f"{Colors.UNDERLINE}{string}{Colors.END}"
    @staticmethod
    def Faint(string: str) -> str:
        return f"{Colors.FAINT}{string}{Colors.END}"
    @staticmethod
    def Italic(string: str) -> str:
        return f"{Colors.ITALIC}{string}{Colors.END}"
    @staticmethod
    def Blink(string: str) -> str:
        return f"{Colors.BLINK}{string}{Colors.END}"
    @staticmethod
    def Inverse(string: str) -> str:
        return f"{Colors.NEGATIVE}{string}{Colors.END}"
    @staticmethod
    def Crossed(string: str) -> str:
        return f"{Colors.CROSSED}{string}{Colors.END}"


class HumanVals:
    '''
        Comes from:  https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb
        Credit to:  Mitch McMabers  for the original version of this code.

        Examples:
            print(HumanVals.format(2251799813685247)) # 2 pebibytes
            print(HumanVals.format(2000000000000000, True)) # 2 petabytes
            print(HumanVals.format(1099511627776)) # 1 tebibyte
            print(HumanVals.format(1000000000000, True)) # 1 terabyte
            print(HumanVals.format(1000000000, True)) # 1 gigabyte
            print(HumanVals.format(4318498233, precision=3)) # 4.022 gibibytes
            print(HumanVals.format(4318498233, True, 3)) # 4.318 gigabytes
            print(HumanVals.format(-4318498233, precision=2)) # -4.02 gibibytes
    '''

    METRIC_LABELS: typing.List[str] = [" ", "K", "M", "G", "T", "P", "E", "Z", "Y"]
    BINARY_LABELS: typing.List[str] = [" ", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi"]
    PRECISION_OFFSETS: typing.List[float] = [0.5, 0.05, 0.005, 0.0005]
    PRECISION_FORMATS: typing.List[str] = ["{}{:.0f} {}", "{}{:.1f} {}", "{}{:.2f} {}", "{}{:.3f} {}"]

    @staticmethod
    def format(num: typing.Union[int, float], metric: bool=False, precision: int=1) -> str:
        """
        Human-readable formatting of bytes, using binary (powers of 1024)
        or metric (powers of 1000) representation.
        """

        assert isinstance(num, (int, float)), "num must be an int or float"
        assert isinstance(metric, bool), "metric must be a bool"
        assert isinstance(precision, int) and precision >= 0 and precision <= 3, "precision must be an int (range 0-3)"

        unit_labels = HumanVals.METRIC_LABELS if metric else HumanVals.BINARY_LABELS
        last_label = unit_labels[-1]
        unit_step = 1000 if metric else 1024
        unit_step_thresh = unit_step - HumanVals.PRECISION_OFFSETS[precision]

        is_negative = num < 0
        if is_negative:
            num = abs(num)

        for unit in unit_labels:
            if num < unit_step_thresh:
                break
            if unit != last_label:
                num /= unit_step

        if unit == " ":
            precision = 0

        return HumanVals.PRECISION_FORMATS[precision].format("-" if is_negative else "", num, unit)


def show_expr(expr, family, args):
    matches = []
    target = None
    c_packets = None
    c_bytes = None
    log = None
    for e in expr:

        if "match" in e:
            left = e["match"]["left"]
            right = e["match"]["right"]

            if "meta" in left:
                if "key" in left["meta"]:
                    left = left["meta"]["key"]

            if "payload" in left:
                left = f"{left['payload']['protocol']} {left['payload']['field']}"
            if "ct" in left:
                left = f"{left['ct']['key']}"

            op = e["match"]["op"]

            if isinstance(right, str):
                if right.startswith('@'):
                    op = "in"
                    right = Colors.LightPurple(right)
            elif isinstance(right, dict):
                if right.get("prefix"):
                    right = f"{right['prefix']['addr']}/{right['prefix']['len']}"
                    op = "in"
                elif right.get("set"):
                    right = str(right["set"])
                    op = "in"
                elif right.get("range"):
                    # Handle range elements like {'range': [0, 1024]}
                    right = f"{right['range'][0]}-{right['range'][1]}"
                    op = "in"
                else:
                    right = str(right)
            else:
                right = str(right)
            matches.append(f"{left} {op} {right}")

        elif "xt" in e:
            if e['xt']['type'] == 'target':
                target = e['xt']['name']
            else:
                matches.append("XT")

        elif "counter" in e:
            c_packets = e['counter']['packets']
            c_bytes = e['counter']['bytes']
            if not args.exact:
                c_packets = HumanVals.format(c_packets, metric=True, precision=1)
                c_bytes = HumanVals.format(c_bytes, metric=True, precision=1)
        elif "jump" in e:
            target = f"{Colors.Purple('jump')} {e['jump']['target']}"
        elif "return" in e:
            target = f"{Colors.Cyan('return')}"
        elif "drop" in e:
            target = f"{Colors.Red('drop')}"
        elif "reject" in e:
            target = f"{Colors.LightRed('reject')}"
        elif "accept" in e:
            target = f"{Colors.Green('accept')}"
        elif "masquerade" in e:
            target = f"{Colors.Yellow('masquerade')}"
        elif "log" in e:
            log = f"level: {e['log'].get('level')}, prefix: \"{e['log'].get('prefix')}\""
        elif "snat" in e or "dnat" in e or "redirect" in e:
            # NAT expressions
            nat_type = "snat" if "snat" in e else ("dnat" if "dnat" in e else "redirect")
            target = Colors.Yellow(nat_type)
        elif "goto" in e:
            target = f"{Colors.Purple('goto')} {e['goto']['target']}"
        elif "queue" in e or "limit" in e or "quota" in e or "notrack" in e:
            # Known expressions we don't need to display as target
            pass
        else:
            # Unknown expression - add to matches for visibility
            matches.append(f"[unknown: {list(e.keys())}]")
    if len(matches) == 0:
        matches.append("*")
    if len(str(matches)) > 60:
        m = "\nAND ".join(matches)
    else:
        m = f" {Colors.LightGray('AND')} ".join(matches)

    return [c_packets, c_bytes, target, log, family, m]


def list_rules(name, table, rules, args, split=False):
    r_table = []
    c_table = []
    t_head = f"Hook: {Colors.Inverse(Colors.Yellow(name))}, Chains: {len(table)}"

    if len(table) > 0:
        for chain in table:
            chain_name = chain[0]
            if args.chain and args.chain != chain_name and args.chain != "all":
                continue
            if args.table and args.table != chain[1]["table"] and args.table != "all":
                continue
            c_table.append([chain[1]["name"], chain[1]["table"], chain[1]["prio"], chain[1].get('policy')])
            if split:
                c_head = tabulate(c_table, headers=["chain", "table", "priority", "default"], numalign="right")
                c_table = []
            if chain_name in rules:
                for rule in rules[chain_name]:
                    try:
                        if rule['rule']['table'] == chain[1]["table"]:
                            tab = show_expr(rule["rule"]["expr"], rule["rule"]["family"], args)
                            r_table.append([rule['rule']['table'], Colors.LightGray(f"{chain_name}/{rule['rule']['handle']}")] + tab)
                    except KeyError as e:
                        # Skip malformed rules but continue processing
                        print(f"Warning: skipping malformed rule in {chain_name}: {e}", file=sys.stderr)
            if split:
                if len(r_table) > 0:
                    if t_head:
                        print(t_head)
                        print("")
                        t_head = None
                    print(c_head)
                    print("")
                    print(tabulate(r_table, headers=["table", "handle", "pkts", "bytes", "target", "log", "proto", "filter"], colalign=("left", "left", "right", "right", "left", "left", "left", "left")))
                    print("")
                    r_table = []
    if not split:
        if len(r_table) > 0:
            print(t_head)
            print("")
            print(tabulate(c_table, headers=["chain", "table", "priority", "default"], numalign="right"))
            print("")
            print(tabulate(r_table, headers=["table", "handle", "pkts", "bytes", "target", "log", "proto", "filter"], colalign=("left", "left", "right", "right", "left", "left", "left", "left")))
            print("")


def show_tables(t_ingress, t_prerouting, t_input, t_forward, t_output, t_postrouting, t_unhooked, rules, args):
    if not args.hook or args.hook == 'all' or args.hook == 'ingress':
        list_rules("ingress", t_ingress, rules, args)
    if not args.hook or args.hook == 'all' or args.hook == 'prerouting':
        list_rules("prerouting", t_prerouting, rules, args)
    if not args.hook or args.hook == 'all' or args.hook == 'input':
        list_rules("input", t_input, rules, args)
    if not args.hook or args.hook == 'all' or args.hook == 'forward':
        list_rules("forward", t_forward, rules, args)
    if not args.hook or args.hook == 'all' or args.hook == 'output':
        list_rules("output", t_output, rules, args)
    if not args.hook or args.hook == 'all' or args.hook == 'postrouting':
        list_rules("postrouting", t_postrouting, rules, args)
    if not args.hook or args.hook == 'all':
        list_rules("unhooked", t_unhooked, rules, args, split=True)


def format_set_element(val):
    """Format a set element value to nft syntax."""
    if isinstance(val, str):
        return val
    elif isinstance(val, int):
        return str(val)
    elif isinstance(val, dict):
        if 'prefix' in val:
            return f"{val['prefix']['addr']}/{val['prefix']['len']}"
        elif 'range' in val:
            return f"{val['range'][0]}-{val['range'][1]}"
        else:
            return str(val)
    else:
        return str(val)


def show_sets(sets, args):
    for set_name, set_values in sets.items():
        if args.set == 'all' or args.set == set_name:
            set_type = set_values.get('type', 'unknown')
            flags = set_values.get('flags', [])
            size = set_values.get('size', 65535)

            # Build set definition
            set_def = f"type {set_type}; size {size};"
            if flags:
                set_def += f" flags {','.join(flags)};"

            print(f"add set {set_values['family']} {set_values['table']} {set_name} {{ {set_def} }}")
            print(f"flush set {set_values['family']} {set_values['table']} {set_name}")

            if 'elem' not in set_values:
                continue

            for elem in set_values['elem']:
                element = None
                comment = None

                if isinstance(elem, (str, int)):
                    element = str(elem)
                elif isinstance(elem, dict):
                    if 'prefix' in elem:
                        element = format_set_element(elem)
                    elif 'range' in elem:
                        element = format_set_element(elem)
                    elif 'elem' in elem:
                        # Wrapped element with metadata
                        elemval = elem['elem']['val']
                        element = format_set_element(elemval)
                        if 'comment' in elem['elem']:
                            comment = elem['elem']['comment']
                    else:
                        element = str(elem)
                else:
                    element = str(elem)

                if element:
                    if comment:
                        print(f"add element {set_values['family']} {set_values['table']} {set_name} {{ {element} comment \"{comment}\" }}")
                    else:
                        print(f"add element {set_values['family']} {set_values['table']} {set_name} {{ {element} }}")


def main():
    parser = argparse.ArgumentParser(
        prog='nft-viewer',
        description='iptables like output of nf_tables',
        epilog='')

    parser.add_argument('-L', '--hook', choices=['all', 'ingress', 'input', 'forward', 'output', 'prerouting', 'postrouting'], help="List only tables for a single hook")
    parser.add_argument('-c', '--chain', help="List only a single chain")
    parser.add_argument('-t', '--table', help="List only a single table")
    parser.add_argument('-s', '--set', nargs='?', action='store', const='all', help="List sets instead of chains and tables")
    parser.add_argument('-x', '--exact', action='store_true', help="Display counters as exact numbers instead of K, M, G etc.")
    parser.add_argument('-j', '--json', action='store_true', help="Output raw JSON")
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    t_ingress = []
    t_prerouting = []
    t_input = []
    t_forward = []
    t_output = []
    t_postrouting = []
    t_unhooked = []

    rules = {}
    tables = {}
    chains = {}
    sets = {}

    nft = nftables.Nftables()
    nft.set_json_output(True)
    nft.set_handle_output(True)
    nft.set_numeric_prio_output(True)

    rc, output, error = nft.cmd("list ruleset")

    if rc != 0:
        if "Permission denied" in str(error) or "Operation not permitted" in str(error):
            print("Permission denied - run with sudo", file=sys.stderr)
        else:
            print(f"nftables error: {error}", file=sys.stderr)
        sys.exit(1)

    try:
        ruleset = json.loads(output)
    except json.JSONDecodeError as e:
        print(f"Unable to parse nftables output: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(ruleset, indent=2))
        sys.exit(0)

    for rule in ruleset['nftables']:
        if "set" in rule:
            sets[rule['set']['name']] = rule['set']
        if "chain" in rule:
            if rule['chain'].get('type') not in chains:
                chains[rule['chain'].get('type')] = {}
            chains[rule['chain'].get('type')][rule['chain']['name']] = rule['chain']
            if "prio" not in rule['chain']:
                chains[rule['chain'].get('type')][rule['chain']['name']]['prio'] = 0
        if "table" in rule:
            tables[rule['table']['name']] = rule['table']
        if "rule" in rule:
            r_chain = rule["rule"]["chain"]
            if r_chain not in rules:
                rules[r_chain] = []
            rules[r_chain].append(rule)

    for t_chains in chains.values():
        sorted_chains = dict(sorted(t_chains.items(), key=lambda x: x[1]['prio']))

        for chain in sorted_chains.items():
            if "hook" in chain[1]:
                if chain[1]["hook"] == "input":
                    t_input.append(chain)
                if chain[1]["hook"] == "output":
                    t_output.append(chain)
                if chain[1]["hook"] == "forward":
                    t_forward.append(chain)
                if chain[1]["hook"] == "ingress":
                    t_ingress.append(chain)
                if chain[1]["hook"] == "prerouting":
                    t_prerouting.append(chain)
                if chain[1]["hook"] == "postrouting":
                    t_postrouting.append(chain)
            else:
                t_unhooked.append(chain)

    if args.set:
        show_sets(sets, args)
    else:
        show_tables(t_ingress, t_prerouting, t_input, t_forward, t_output, t_postrouting, t_unhooked, rules, args)


if __name__ == "__main__":
    main()
