import sys
import os

from algoritmo_genetico import AlgoritmoGenetico
from ambiente import Ambiente
from config import ARQUIVO_CHECKPOINT
import pickle

def assistir_melhor():
    if not os.path.exists(ARQUIVO_CHECKPOINT):
        print("Nenhum checkpoint encontrado. Execute o programa para evoluir um indivíduo primeiro.")
        return

    with open(ARQUIVO_CHECKPOINT, 'rb') as f:
        estado = pickle.load(f)

    melhor = estado.get('melhor_global')
    if melhor is None:
        print("Não há melhor indivíduo salvo ainda.")
        return

    print(f"Assistindo o melhor indivíduo (geração {estado['geracao_atual']})...")
    print(f"  Fitness: {melhor.fitness:.2f}")
    print(f"  Distância: {melhor.distancia_percorrida}")
    print(f"  Venceu: {'SIM' if melhor.venceu else 'NAO'}")

    ambiente = Ambiente(renderizar=True)
    try:
        ambiente.avaliar_individuo(melhor)
    finally:
        ambiente.fechar()


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ('--assistir', '--watch', '-a'):
        assistir_melhor()
        return

    ag = AlgoritmoGenetico()
    ag.executar()

if __name__ == '__main__':
    main()
