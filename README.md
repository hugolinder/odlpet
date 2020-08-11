Python bindings for [STIR](http://stir.sourceforge.net/) based on [ODL](https://odlgroup.github.io/odl/).

Extracted from [a stir branch of odl](https://github.com/NikEfth/odl/tree/_stir_backend) with

```sh
git filter-branch --index-filter 'git rm --cached -qr --ignore-unmatch -- . && git reset -q $GIT_COMMIT -- test/tomo/backends/stir_setup_test.py odl/test/largescale/tomo/stir_slow_test.py odl/tomo/backends/stir_bindings.py odl/tomo/backends/stir_setup.py examples/tomo/stir_reconstruct.py examples/tomo/stir_project.py examples/tomo/data/stir/initial.hv examples/tomo/data/stir/initial.v examples/tomo/data/stir/small.hs examples/tomo/data/stir/small.s' --prune-empty -- --all
```

installation without pip or conda

1. Download the package
2. unzip it if it is zipped
3. cd into the directory containing setup.py
4. If there are any installation instructions contained in documentation contianed herein, read and follow the instructions OTHERWISE
5. type in python setup.py install
