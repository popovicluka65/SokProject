from setuptools import setup, find_packages

setup(
    name="graph-parser-json",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['Projekat', 'Projekat.Sok', 'Projekat.Sok.Plagini'],
    # Grupa za prikazivanje fakulteta
    # `prikaz_obican` je alias za rs.uns.ftn.fakultet.prikaz_obican:FakultetPrikazObican
    entry_points={
        'graph.parser':
            ['parser_JSON=Projekat.Sok.Plagini.graphParserJSON:GraphParserJSON'],
    },
    data_files=[('file',['file/example1.json','file/config.json'])],
    install_requires=[
        'projekat-sok-api==0.1',
    ],
    zip_safe=True
)