# nft-viewer

> [!IMPORTANT]
> This project is NOT part of the official [nftables](https://netfilter.org/projects/nftables/index.html) project

A simple tool to display information from nf-tables in a more iptables-like format.

## Installation

**Requirements:** `python3-nftables` system package must be installed.

```bash
# Fedora/RHEL
dnf install python3-nftables

# Debian/Ubuntu
apt install python3-nftables
```

**Install from private registry:**

```bash
uv tool install --extra-index-url https://git.olen.net/api/packages/Olen/pypi/simple/ nft-viewer
```

**Or install from source:**

```bash
git clone https://git.olen.net/olen/nftables.git
cd nftables
uv tool install .
```

## Usage

```bash
nft-viewer              # Show all rules
nft-viewer -L input     # Show only input hook
nft-viewer -s           # Show all sets
nft-viewer -s my-set    # Show specific set
nft-viewer -j           # Output raw JSON
nft-viewer -x           # Show exact counter values (no K/M/G)
```

## Overview

This tool

It complements the official `nft` tool, and tries to find a space between `nft` - where the output can be quite complex to follow, and `iptables-nft` - which I felt was to limited.

The tool is not designed to modify nf-tables rules, only to display them in an easy to understand format.

You can chose to display the entire ruleset, or just a single `hook` (input, output, forward, prerouting, postrouting), a single chain, or a set.

## Examples

### Display a single hook

nft-viewer -L input
```
hook      # chains
------  ----------
input            3

chain      table        priority  default
---------  ---------  ----------  ---------
MYCHAIN    filter            -10  accept
f2b-chain  f2b-table          -1  accept
INPUT      filter              0  accept

handle         pkts    bytes  target    log    proto    filter
-----------  ------  -------  --------  -----  -------  --------------------------------------------------
MYCHAIN/9    74.2 K   18.9 M  accept           inet     ip saddr == @my-set
f2b-chain/3      27    1.6 K  reject           inet     l4proto == tcp AND ip saddr == @addr-set-blacklist
f2b-chain/5       0        0  reject           inet     tcp dport == 143 AND ip saddr == @addr-set-dovecot
f2b-chain/7      20    1.6 K  reject           inet     tcp dport == 22 AND ip saddr == @addr-set-sshd
INPUT/132    18.7 K  832.9 K  reject           ip       ip saddr == @abuseipdb
INPUT/166         0        0  drop             ip       ip saddr == @fedotracker
INPUT/171         0        0  drop             ip       ip saddr == @talos
INPUT/174         0        0  drop             ip       ip saddr == @threatfox


```

sudo nft-viewer -L forward                                                                                    
```
hook       # chains                                                                                                            
-------  ----------                                                                                                            
forward           2                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                              
chain            table      priority  default                                                                                  
---------------  -------  ----------  ---------                                                                                
OLENNET_FORWARD  filter          -10  accept                                                                                                                                                                                                                  
FORWARD          filter            0  drop                                                                                                                                                                                                                    
                                                                                                                               
handle                 pkts    bytes  target                         log    proto    filter                    
------------------  -------  -------  -----------------------------  -----  -------  ---------------------------------------------------------
FORWARD/13                0        0  accept                                inet     iifname == eth1 AND oifname == eth0
FORWARD/68            9.6 K  862.1 K  accept                                ip6      ip6 saddr == fd00:ffff:42::/48
FORWARD/182               0        0  accept                                ip6      state in ['established', 'related']
FORWARD/183               0        0  accept                                ip       state in ['established', 'related']
FORWARD/417               0        0  jump DOCKER                           ip       oifname == docker0

```

If your terminal supports color, the output is even easier to read:

![image](https://github.com/Olen/nftables/assets/203184/465644a1-3d60-481a-8fdf-108ec682dfd9)



The output is ordered according to the chain priority, and you can easily get a good overview over what chains and rules are in use and how they are configured.

### Display a set

nft-viewer -s my-set
```
add set inet filter my-set { type ipv4_addr; size 65536; }
flush set inet filter my-set
add element inet filter my-set { 10.20.0.0/16 comment "network 1" }
add element inet filter my-set { 10.40.0.0/16 comment "another network" }
add element inet filter my-set { 172.16.0.0/16 comment "lan" }
```

Output here is actually the format to recreate the set, so you can easily run this command and redirect to a file (`nft-viewer -s my-set > my-set.nft`, add or modify entries, and just run `nft -f my-set.nft` to update it.


## Acknowledgments

After searching and discovering [nftwatch](https://github.com/flyingrhinonz/nftwatch) I was inspired to create something even simpler and more familiar when you come from an iptables-background, without all the limits of `iptables-nft`

