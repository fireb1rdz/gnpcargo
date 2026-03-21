class DocumentImporterRegistry:
    _importers = []

    @classmethod
    def register(cls, importer):
        cls._importers.append(importer)

    @classmethod
    def get_importer(cls, root):
        for importer in cls._importers:
            if importer.can_import(root):
                return importer
        raise ValueError("Tipo de documento fiscal não suportado")
