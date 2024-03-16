from schemas.serialization import SchemaSerializeDocJsonTimes


_schema = SchemaSerializeDocJsonTimes()
docJsonDates = lambda d: _schema.dump(d)
