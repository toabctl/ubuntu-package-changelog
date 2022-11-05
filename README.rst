ubuntu-package-changelog
------------------------

`ubuntu-package-changelog` can be used to get a changelog for
a given Ubuntu source package. Eg::

  ubuntu-package-changelog focal Updates linux-azure
  linux-azure (5.4.0-1043.45) focal; urgency=medium

    [ Ubuntu: 5.4.0-70.78 ]

    * CVE-2020-27170
      - bpf: Fix off-by-one for area size in creating mask to left
    * CVE-2020-27171
      - bpf: Prohibit alu ops for pointer types not defining ptr_limit
    * binary assembly failures with CONFIG_MODVERSIONS present (LP: #1919315)
      - [Packaging] quiet (nomially) benign errors in BUILD script

   -- Thadeu Lima de Souza Cascardo <cascardo@canonical.com>  Fri, 19 Mar 2021 13:32:55 -0300

By default, only the latest changelog entry is shown. To see more entries, use the `--entries`
flag.
It's also possible to get a changelog for a package in a PPA::

  ubuntu-package-changelog -ppa cloud-images/eks-01.11.0 focal Release cni
  cni (0.6.0-0ubuntu1) bionic; urgency=medium
  [...]

It's also possible to list changelog entries for private PPAs. For that, `--lp-user`
must be given. Eg::

  ubuntu-package-changelog --lp-user toabctl --ppa fips-cc-stig/cc bionic Release fips-initramfs
  fips-initramfs (0.0.11~rc5) bionic; urgency=medium
  [...]


`ubuntu-package-changelog` can be also used to highlight the CVEs referenced in a changelog for
a given Ubuntu source package. Note this also shows the CVE priority assigned by the Ubuntu security team. Eg::

    ubuntu-package-changelog --highlight-cves focal Updates linux-azure
    linux-azure (5.4.0-1094.100) focal; urgency=medium

      CVEs addressed/mitigated in linux-azure version 5.4.0-1094.100:
        CVE-2022-2602 (high priority)
        CVE-2022-41674 (medium priority)
        CVE-2022-42721 (medium priority)
        CVE-2022-42720 (medium priority)

      [ Ubuntu: 5.4.0-131.147 ]

      * CVE-2022-2602
        - SAUCE: io_uring/af_unix: defer registered files gc to io_uring release
        - SAUCE: io_uring/af_unix: fix memleak during unix GC
      * CVE-2022-41674
        - SAUCE: wifi: cfg80211: fix u8 overflow in
          cfg80211_update_notlisted_nontrans()
        - SAUCE: wifi: cfg80211/mac80211: reject bad MBSSID elements
        - SAUCE: wifi: cfg80211: ensure length byte is present before access
        - SAUCE: wifi: mac80211_hwsim: avoid mac80211 warning on bad rate
        - SAUCE: wifi: cfg80211: update hidden BSSes to avoid WARN_ON
      * CVE-2022-42721
        - SAUCE: wifi: cfg80211: avoid nontransmitted BSS list corruption
      * CVE-2022-42720
        - SAUCE: wifi: cfg80211: fix BSS refcounting bugs

     -- Thadeu Lima de Souza Cascardo <cascardo@canonical.com>  Sun, 16 Oct 2022 23:55:23 -0300

If you wish to use `ubuntu-package-changelog` to show CVE descriptions when highlighting the CVEs referenced in a changelog for
a given Ubuntu source package. Eg::

    ubuntu-package-changelog --highlight-cves --highlight-cves-show-cve-description focal Updates linux-azure
    linux-azure (5.4.0-1094.100) focal; urgency=medium

      CVEs addressed/mitigated in linux-azure version 5.4.0-1094.100:
        CVE-2022-2602 (high priority):  David Bouman and Billy Jheng Bing Jhong discovered that a race condition existed in the io_uring subsystem in the Linux kernel, leading to a use- after-free vulnerability. A local attacker could use this to cause a denial of service (system crash) or possibly execute arbitrary code.
        CVE-2022-41674 (medium priority):  Sönke Huster discovered that an integer overflow vulnerability existed in the WiFi driver stack in the Linux kernel, leading to a buffer overflow. A physically proximate attacker could use this to cause a denial of service (system crash) or possibly execute arbitrary code.
        CVE-2022-42721 (medium priority):  Sönke Huster discovered that the WiFi driver stack in the Linux kernel did not properly handle BSSID/SSID lists in some situations. A physically proximate attacker could use this to cause a denial of service (infinite loop).
        CVE-2022-42720 (medium priority):  Sönke Huster discovered that the WiFi driver stack in the Linux kernel did not properly perform reference counting in some situations, leading to a use-after-free vulnerability. A physically proximate attacker could use this to cause a denial of service (system crash) or possibly execute arbitrary code.

      [ Ubuntu: 5.4.0-131.147 ]

      * CVE-2022-2602
        - SAUCE: io_uring/af_unix: defer registered files gc to io_uring release
        - SAUCE: io_uring/af_unix: fix memleak during unix GC
      * CVE-2022-41674
        - SAUCE: wifi: cfg80211: fix u8 overflow in
          cfg80211_update_notlisted_nontrans()
        - SAUCE: wifi: cfg80211/mac80211: reject bad MBSSID elements
        - SAUCE: wifi: cfg80211: ensure length byte is present before access
        - SAUCE: wifi: mac80211_hwsim: avoid mac80211 warning on bad rate
        - SAUCE: wifi: cfg80211: update hidden BSSes to avoid WARN_ON
      * CVE-2022-42721
        - SAUCE: wifi: cfg80211: avoid nontransmitted BSS list corruption
      * CVE-2022-42720
        - SAUCE: wifi: cfg80211: fix BSS refcounting bugs

     -- Thadeu Lima de Souza Cascardo <cascardo@canonical.com>  Sun, 16 Oct 2022 23:55:23 -0300


If you wish to use `ubuntu-package-changelog` to only show referenced CVEs in a changelog for
a given Ubuntu source package. Eg::

    ubuntu-package-changelog --highlight-cves-only focal Updates linux-azure
    linux-azure (5.4.0-1094.100) focal; urgency=medium

      CVEs addressed/mitigated in linux-azure version 5.4.0-1094.100:
        CVE-2022-2602 (high priority)
        CVE-2022-41674 (medium priority)
        CVE-2022-42721 (medium priority)
        CVE-2022-42720 (medium priority)

     -- Thadeu Lima de Souza Cascardo <cascardo@canonical.com>  Sun, 16 Oct 2022 23:55:23 -0300

This `--highlight-cves-only` flag can be used in conjunction with `--highlight-cves-show-cve-description` to only show referenced CVEs in a changelog and also include the CVE description. Eg::

    ubuntu-package-changelog --highlight-cves-only --highlight-cves-show-cve-description focal Updates linux-azure
    linux-azure (5.4.0-1094.100) focal; urgency=medium

      CVEs addressed/mitigated in linux-azure version 5.4.0-1094.100:
        CVE-2022-2602 (high priority):  David Bouman and Billy Jheng Bing Jhong discovered that a race condition existed in the io_uring subsystem in the Linux kernel, leading to a use- after-free vulnerability. A local attacker could use this to cause a denial of service (system crash) or possibly execute arbitrary code.
        CVE-2022-41674 (medium priority):  Sönke Huster discovered that an integer overflow vulnerability existed in the WiFi driver stack in the Linux kernel, leading to a buffer overflow. A physically proximate attacker could use this to cause a denial of service (system crash) or possibly execute arbitrary code.
        CVE-2022-42721 (medium priority):  Sönke Huster discovered that the WiFi driver stack in the Linux kernel did not properly handle BSSID/SSID lists in some situations. A physically proximate attacker could use this to cause a denial of service (infinite loop).
        CVE-2022-42720 (medium priority):  Sönke Huster discovered that the WiFi driver stack in the Linux kernel did not properly perform reference counting in some situations, leading to a use-after-free vulnerability. A physically proximate attacker could use this to cause a denial of service (system crash) or possibly execute arbitrary code.

     -- Thadeu Lima de Souza Cascardo <cascardo@canonical.com>  Sun, 16 Oct 2022 23:55:23 -0300

Installation
============

`ubuntu-package-changelog` is available as snap.

|Get it from the Snap Store|

For installation, do::

  snap install ubuntu-package-changelog

To access private PPAs, it's useful to connect the `password-manager-service`
so authorization is only done once::

  snap connect ubuntu-package-changelog:password-manager-service

The other option is installing it into a `virtualenv`::

  virtualenv venv
  source venv/bin/activate
  pip install -e .
  # now you can use the tool
  ubuntu-package-changelog -h

Contributions
=============

Please use github (https://github.com/toabctl/ubuntu-package-changelog) issues
and pull requests for discussions and contribution.


.. |Get it from the Snap Store| image:: https://snapcraft.io/static/images/badges/en/snap-store-white.svg
   :target: https://snapcraft.io/ubuntu-package-changelog
