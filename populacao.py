import random
from individuo import Individuo
from config import (
    TAMANHO_POPULACAO,
    TAMANHO_CROMOSSOMO,
    TAXA_MUTACAO,
    TAXA_CROSSOVER,
    TAMANHO_ELITE,
    TAMANHO_TORNEIO,
    INDIVIDUOS_NOVOS_AO_AGITAR,
)

class Populacao:

    def __init__(self, tamanho=TAMANHO_POPULACAO, criar_aleatoria=True):

        self.tamanho = tamanho
        self.individuos = []

        if criar_aleatoria:
            self._criar_populacao_inicial()

    def _criar_populacao_inicial(self):
        self.individuos = [Individuo() for _ in range(self.tamanho)]

    def ordenar_por_fitness(self):
        self.individuos.sort(key=lambda ind: ind.fitness, reverse=True)

    def melhor_individuo(self):

        return max(self.individuos, key=lambda ind: ind.fitness)

    def fitness_media(self):
        if not self.individuos:
            return 0.0
        return sum(ind.fitness for ind in self.individuos) / len(self.individuos)

    def selecao_torneio(self, tamanho_torneio=TAMANHO_TORNEIO):

        competidores = random.sample(self.individuos, tamanho_torneio)
        return max(competidores, key=lambda ind: ind.fitness)

    def crossover(self, pai1, pai2):

        if random.random() > TAXA_CROSSOVER:
            return pai1.clonar(), pai2.clonar()

        ponto1 = random.randint(0, TAMANHO_CROMOSSOMO - 1)
        ponto2 = random.randint(ponto1, TAMANHO_CROMOSSOMO - 1)

        cromossomo_filho1 = (
            pai1.cromossomo[:ponto1]
            + pai2.cromossomo[ponto1:ponto2]
            + pai1.cromossomo[ponto2:]
        )
        cromossomo_filho2 = (
            pai2.cromossomo[:ponto1]
            + pai1.cromossomo[ponto1:ponto2]
            + pai2.cromossomo[ponto2:]
        )

        filho1 = Individuo(cromossomo=cromossomo_filho1)
        filho2 = Individuo(cromossomo=cromossomo_filho2)

        return filho1, filho2

    def evoluir(self, taxa_mutacao=TAXA_MUTACAO, modo_agitacao=False):

        nova_populacao = Populacao(tamanho=self.tamanho, criar_aleatoria=False)

        self.ordenar_por_fitness()
        melhor = self.individuos[0]

        for i in range(TAMANHO_ELITE):
            nova_populacao.individuos.append(self.individuos[i].clonar())

        num_variantes_focadas = max(self.tamanho // 3, 5)
        ponto_inicio = max(melhor.gene_da_max_pos - 5, 0)

        for _ in range(num_variantes_focadas):
            if len(nova_populacao.individuos) >= self.tamanho:
                break
            variante = melhor.clonar()
            taxa_focada = 0.30 if modo_agitacao else 0.15
            variante.mutar_a_partir_de(ponto_inicio, taxa_focada)
            nova_populacao.individuos.append(variante)

        if modo_agitacao:
            for _ in range(INDIVIDUOS_NOVOS_AO_AGITAR):
                if len(nova_populacao.individuos) < self.tamanho:
                    nova_populacao.individuos.append(Individuo())

        while len(nova_populacao.individuos) < self.tamanho:
            pai1 = self.selecao_torneio()
            pai2 = self.selecao_torneio()

            filho1, filho2 = self.crossover(pai1, pai2)

            filho1.mutar(taxa_mutacao)
            filho2.mutar(taxa_mutacao)

            nova_populacao.individuos.append(filho1)
            if len(nova_populacao.individuos) < self.tamanho:
                nova_populacao.individuos.append(filho2)

        return nova_populacao

    def __len__(self):
        return len(self.individuos)