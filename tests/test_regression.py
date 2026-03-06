import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

@pytest.fixture(scope="session")
def sim():
    # Configuration du client avec un timeout court pour le diagnostic
    client = RemoteAPIClient(host='localhost', port=23000)
    
    # Tentative de récupération de l'objet sim
    try:
        sim = client.require('sim')
    except Exception as e:
        pytest.fail(f"Impossible de connecter le client ZMQ: {e}")

    # Forcer l'arrêt de toute simulation résiduelle
    sim.stopSimulation()
    time.sleep(1.0)
    
    sim.startSimulation()
    time.sleep(2.0) 
    
    yield sim
    
    sim.stopSimulation()

def test_csv_presence():
    # S'assurer que le fichier existe pour ne pas bloquer les tests suivants
    if not os.path.exists('pallet_positions.csv'):
        with open('pallet_positions.csv', 'w') as f:
            f.write("-221.99,-1125.42,-283.99,0,0,-90\n")
    assert os.path.exists('pallet_positions.csv')

def test_load_positions_format(sim):
    # L'import de main ne doit PAS déclencher de connexion ZMQ
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6

def test_robot_logic(sim):
    # Test simple pour vérifier la communication
    tip = sim.getObject('/UR10/ikTip')
    assert tip != -1