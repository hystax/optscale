import optscale_arcee as arcee

arcee.init("test", "test")
arcee.tag("key", "value")
arcee.tag("test1", "test2")
arcee.milestone("just a milestone")
arcee.send({"t": 2})
arcee.finish()
print(arcee.info())
