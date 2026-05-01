import random
import numpy as np
from config import TAMANHO_CROMOSSOMO, NUM_ACOES

class Individuo:

    def __init__(self, cromossomo=None):

        if cromossomo is None:
            self.cromossomo = self._gerar_cromossomo_aleatorio()
        else:
            self.cromossomo = cromossomo

        self.fitness = 0.0
        self.distancia_percorrida = 0
        self.venceu = False
        self.morreu = False
        self.moedas = 0
        self.pontuacao = 0
        self.tempo_restante = 0
        self.gene_da_morte = 0      
        self.gene_da_max_pos = 0    

    def _gerar_cromossomo_aleatorio(self):

        return [random.randint(0, NUM_ACOES - 1) for _ in range(TAMANHO_CROMOSSOMO)]

    def mutar(self, taxa_mutacao):

        for i in range(len(self.cromossomo)):
            if random.random() < taxa_mutacao:
                self.cromossomo[i] = random.randint(0, NUM_ACOES - 1)

    def mutar_a_partir_de(self, ponto_inicio, taxa_mutacao):

        ponto_inicio = max(0, min(ponto_inicio, len(self.cromossomo) - 1))

        for i in range(ponto_inicio, len(self.cromossomo)):
            if random.random() < taxa_mutacao:
                self.cromossomo[i] = random.randint(0, NUM_ACOES - 1)

    def clonar(self):

        novo = Individuo(cromossomo=self.cromossomo.copy())
        novo.fitness = self.fitness
        novo.distancia_percorrida = self.distancia_percorrida
        novo.venceu = self.venceu
        novo.morreu = self.morreu
        novo.moedas = self.moedas
        novo.pontuacao = self.pontuacao
        novo.tempo_restante = self.tempo_restante
        novo.gene_da_morte = self.gene_da_morte
        novo.gene_da_max_pos = self.gene_da_max_pos
        return novo

    def __repr__(self):
        return (f"Individuo(fitness={self.fitness:.2f}, "
                f"distancia={self.distancia_percorrida}, "
                f"venceu={self.venceu})")