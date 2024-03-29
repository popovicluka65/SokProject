from setuptools import setup, find_packages

setup(
    name="graph-visualiser-simple",
    version="0.1",
    packages=find_packages(),
    namespace_packages=['Projekat', 'Projekat.Sok', 'Projekat.Sok.Plagini'],
    # Grupa za prikazivanje fakulteta
    # `prikaz_obican` je alias za rs.uns.ftn.fakultet.prikaz_obican:FakultetPrikazObican
    entry_points={
        'graph.visualiser':
            ['visualiser_simple=Projekat.Sok.Plagini.graphVisualiserSimple:GraphVisualiserSimple'],
    },
    data_files=[('template', ['template/simple_visualizer.html'])],
    install_requires=[
        'projekat-sok-api==0.1',
    ],
    zip_safe=True
)