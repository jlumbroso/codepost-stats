
def test_import_all():

    # ignore the deprecation warnings of yaql and aoihttp
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    import codepost_stats
    import codepost_stats.analyzers.abstract.base
    import codepost_stats.analyzers.abstract.simple
    import codepost_stats.analyzers.abstract
    import codepost_stats.analyzers.standard
    import codepost_stats.analyzers.pool
    import codepost_stats.helpers
    import codepost_stats.event_loop

    assert True
