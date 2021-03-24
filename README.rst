ubuntu-package-changelog
------------------------

`ubuntu-package-changelog` can be used to get a changelog for
a given Ubuntu source package. Eg::

  ubuntu-package-changelog focal Updates linux-azure --lines 12
  linux-azure (5.4.0-1043.45) focal; urgency=medium

    [ Ubuntu: 5.4.0-70.78 ]

    * CVE-2020-27170
      - bpf: Fix off-by-one for area size in creating mask to left
    * CVE-2020-27171
      - bpf: Prohibit alu ops for pointer types not defining ptr_limit
    * binary assembly failures with CONFIG_MODVERSIONS present (LP: #1919315)
      - [Packaging] quiet (nomially) benign errors in BUILD script

   -- Thadeu Lima de Souza Cascardo <cascardo@canonical.com>  Fri, 19 Mar 2021 13:32:55 -0300

Installation
============

Curently, installing into a `virtualenv` is the best thing todo::

  virtualenv venv
  source venv/bin/activate
  pip install -e .
  # now you can use the tool
  ubuntu-package-changelog -h

Contributions
=============

Please use github (https://github.com/toabctl/ubuntu-package-changelog) issues
and pull requests for discussions and contribution.
