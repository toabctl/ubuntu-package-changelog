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

Installation
============

`ubuntu-package-changelog` is available as snap.

|Get it from the Snap Store|

For installation, do::

  snap install ubuntu-package-changelog

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
