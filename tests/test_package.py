def test_import_star():
    """
    Test that `from svg.charts import *` imports all the modules
    """
    mod_src = 'from svg.charts import *\n'
    code = compile(mod_src, 'test_import_star_module.py', 'exec')
    ns = {}
    exec(code, ns)
    assert 'graph' in ns
    assert 'plot' in ns
