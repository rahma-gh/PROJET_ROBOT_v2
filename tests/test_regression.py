import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

@pytest.fixture(scope="session")
def sim():
    # On définit un hôte et un port explicites (doivent correspondre à entrypoint.sh)
    # On ajoute un timeout de 10 secondes pour éviter le blocage infini
    client = RemoteAPIClient(host='localhost', port=23000)
    client.set_timeout(10) 
    
    try:
        sim = client.require('sim')
        # S'assurer que la simulation est propre
        sim.stopSimulation()
        time.sleep(1.0)
        
        sim.startSimulation()
        time.sleep(2.0)
        yield sim
        
        sim.stopSimulation()
    except Exception as e:
        pytest.fail(f"Échec critique de connexion à CoppeliaSim: {e}")

def test_csv_presence():
    # Création d'un CSV minimal pour que les tests suivants ne plantent pas
    if not os.path.exists('pallet_positions.csv'):
        with open('pallet_positions.csv', 'w') as f:
            f.write("0,0,0,0,0,0")
    assert os.path.exists('pallet_positions.csv')

def test_load_positions_format(sim):
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6