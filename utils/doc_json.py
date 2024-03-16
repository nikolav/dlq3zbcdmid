from schemas.serialization import SchemaSerializeDocJson


_schema = SchemaSerializeDocJson()
docJson = lambda d: _schema.dump(d)
