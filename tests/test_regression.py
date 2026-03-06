import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

@pytest.fixture(scope="session")
def sim():
    # Connexion simple
    client = RemoteAPIClient(host='localhost', port=23000)
    
    try:
        # On tente de récupérer l'objet sim
        sim = client.require('sim')
        
        # On force un arrêt/départ pour nettoyer l'état de la scène
        sim.stopSimulation()
        time.sleep(1.0)
        
        sim.startSimulation()
        time.sleep(2.0)
        yield sim
        
        sim.stopSimulation()
    except Exception as e:
        pytest.fail(f"Erreur de connexion ZMQ au serveur : {e}")

def test_csv_presence():
    assert os.path.exists('pallet_positions.csv')

def test_load_positions_format(sim):
    from main import LoadPalletPosition
    # Vérifie que la fonction peut charger les données sans planter
    positions = LoadPalletPosition()
    assert isinstance(positions, list)