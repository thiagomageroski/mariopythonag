import os
import pickle
import time

from populacao import Populacao
from ambiente import Ambiente
from individuo import Individuo
from estatisticas import Estatisticas
from config import (
    NUMERO_GERACOES,
    TAMANHO_POPULACAO,
    PASTA_RESULTADOS,
    ARQUIVO_CHECKPOINT,
    ARQUIVO_HISTORICO,
    SALVAR_A_CADA,
    RENDERIZAR,
    RENDERIZAR_SO_MELHOR,
    TAXA_MUTACAO,
    TAXA_MUTACAO_AGITADA,
    GERACOES_PARA_AGITAR,
)

class AlgoritmoGenetico:

    def __init__(self):
        self.populacao = None
        self.geracao_atual = 0
        self.melhor_global = None
        self.historico = []
        self.geracoes_sem_melhora = 0

        os.makedirs(PASTA_RESULTADOS, exist_ok=True)

        self.ambiente = Ambiente(renderizar=RENDERIZAR)

    def salvar_checkpoint(self):

        estado = {
            'geracao_atual': self.geracao_atual,
            'populacao': self.populacao,
            'melhor_global': self.melhor_global,
            'historico': self.historico,
        }
        with open(ARQUIVO_CHECKPOINT, 'wb') as f:
            pickle.dump(estado, f)
        print(f"[Checkpoint] Geração {self.geracao_atual} salva em {ARQUIVO_CHECKPOINT}")

    def carregar_checkpoint(self):

        if not os.path.exists(ARQUIVO_CHECKPOINT):
            return False

        try:
            with open(ARQUIVO_CHECKPOINT, 'rb') as f:
                estado = pickle.load(f)
            self.geracao_atual = estado['geracao_atual']
            self.populacao = estado['populacao']
            self.melhor_global = estado['melhor_global']
            self.historico = estado['historico']
            print(f"[Checkpoint] Continuando da geração {self.geracao_atual}")
            print(f"[Checkpoint] Melhor fitness até agora: {self.melhor_global.fitness:.2f}")
            return True
        except Exception as e:
            print(f"[Checkpoint] Erro ao carregar: {e}")
            return False

    def salvar_historico(self):
        with open(ARQUIVO_HISTORICO, 'w') as f:
            f.write("Geracao;FitnessMelhor;FitnessMedia;DistanciaMelhor;Venceu\n")
            for entrada in self.historico:
                f.write(
                    f"{entrada['geracao']};"
                    f"{entrada['fitness_melhor']:.2f};"
                    f"{entrada['fitness_media']:.2f};"
                    f"{entrada['distancia_melhor']};"
                    f"{entrada['venceu']}\n"
                )

    def avaliar_populacao(self):

        print(f"\n--- Avaliando Geração {self.geracao_atual} ---")

        for i, individuo in enumerate(self.populacao.individuos):
            if RENDERIZAR_SO_MELHOR:
                pass

            inicio = time.time()
            self.ambiente.avaliar_individuo(individuo)
            duracao = time.time() - inicio

            print(
                f"  Indivíduo {i+1:02d}/{len(self.populacao)}: "
                f"fitness={individuo.fitness:8.2f} | "
                f"distância={individuo.distancia_percorrida:4d} | "
                f"moedas={individuo.moedas} | "
                f"venceu={'SIM' if individuo.venceu else 'NAO'} | "
                f"tempo={duracao:.1f}s"
            )

    def atualizar_estatisticas(self):

        melhor_atual = self.populacao.melhor_individuo()
        media_atual = self.populacao.fitness_media()

        if self.melhor_global is None or melhor_atual.fitness > self.melhor_global.fitness:
            self.melhor_global = melhor_atual.clonar()
            self.geracoes_sem_melhora = 0
            print(f"  >>> NOVO MELHOR GLOBAL! Fitness: {self.melhor_global.fitness:.2f} "
                  f"| Distância: {self.melhor_global.distancia_percorrida}")
        else:
            self.geracoes_sem_melhora += 1
            print(f"  (sem melhora há {self.geracoes_sem_melhora} gerações)")

        entrada = {
            'geracao': self.geracao_atual,
            'fitness_melhor': melhor_atual.fitness,
            'fitness_media': media_atual,
            'distancia_melhor': melhor_atual.distancia_percorrida,
            'venceu': melhor_atual.venceu,
        }
        self.historico.append(entrada)

        print(f"\n  RESUMO Geração {self.geracao_atual}:")
        print(f"    Melhor fitness:  {melhor_atual.fitness:.2f}")
        print(f"    Fitness média:   {media_atual:.2f}")
        print(f"    Maior distância: {melhor_atual.distancia_percorrida}")
        print(f"    Venceu fase:     {'SIM' if melhor_atual.venceu else 'NAO'}")

    def executar(self):

        print("=" * 70)
        print(" ALGORITMO GENÉTICO - SUPER MARIO BROS ")
        print("=" * 70)

        carregou = self.carregar_checkpoint()
        if not carregou:
            print("Iniciando nova evolução do zero...")
            self.populacao = Populacao(tamanho=TAMANHO_POPULACAO)
            self.geracao_atual = 0

        try:
            while self.geracao_atual < NUMERO_GERACOES:
                self.geracao_atual += 1

                self.avaliar_populacao()

                self.atualizar_estatisticas()

                if self.geracao_atual % SALVAR_A_CADA == 0:
                    self.salvar_checkpoint()
                    self.salvar_historico()

                if self.geracao_atual < NUMERO_GERACOES:
                    deve_agitar = self.geracoes_sem_melhora >= GERACOES_PARA_AGITAR
                    if deve_agitar:
                        print(f"\n  >>> AGITANDO POPULAÇÃO! "
                              f"({self.geracoes_sem_melhora} gerações sem melhora) <<<")
                        print(f"      Mutação alta + sangue novo para desentravar...")
                        taxa_mut = TAXA_MUTACAO_AGITADA
                        self.geracoes_sem_melhora = 0
                    else:
                        taxa_mut = TAXA_MUTACAO

                    self.populacao = self.populacao.evoluir(
                        taxa_mutacao=taxa_mut,
                        modo_agitacao=deve_agitar,
                    )

        except KeyboardInterrupt:
            print("\n\n[INTERRUPÇÃO] Salvando progresso antes de sair...")
            self.salvar_checkpoint()
            self.salvar_historico()
            print("Progresso salvo. Você pode retomar executando o programa novamente.")

        finally:
            self.ambiente.fechar()

            print("\n[ESTATÍSTICAS] Gerando relatório e gráficos finais...")
            try:
                stats = Estatisticas(
                    historico=self.historico,
                    melhor_global=self.melhor_global,
                )
                stats.gerar_tudo()
            except Exception as e:
                print(f"Aviso: erro ao gerar estatísticas ({e}).")

            print("\n" + "=" * 70)
            if self.melhor_global is not None:
                print(f"MELHOR INDIVÍDUO ENCONTRADO:")
                print(f"  Fitness:    {self.melhor_global.fitness:.2f}")
                print(f"  Distância:  {self.melhor_global.distancia_percorrida}")
                print(f"  Moedas:     {self.melhor_global.moedas}")
                print(f"  Venceu:     {'SIM' if self.melhor_global.venceu else 'NAO'}")
            print("=" * 70)