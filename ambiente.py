import gym_super_mario_bros
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT
from nes_py.wrappers import JoypadSpace

from config import (
    NOME_FASE,
    PESO_DISTANCIA,
    PESO_TEMPO,
    PESO_MOEDAS,
    PESO_PONTUACAO,
    BONUS_VITORIA,
    PENALIDADE_MORTE,
    FRAME_SKIP,
)

class Ambiente:

    def __init__(self, renderizar=False):

        self.renderizar = renderizar
        self.env = None
        self._criar_ambiente()

    def _criar_ambiente(self):
        modo = 'human' if self.renderizar else 'rgb_array'

        try:
            self.env = gym_super_mario_bros.make(NOME_FASE, render_mode=modo, apply_api_compatibility=True)
        except TypeError:
            self.env = gym_super_mario_bros.make(NOME_FASE)

        self.env = JoypadSpace(self.env, SIMPLE_MOVEMENT)

    def avaliar_individuo(self, individuo):

        try:
            obs = self.env.reset()
            if isinstance(obs, tuple):
                obs = obs[0]
        except Exception:
            obs = self.env.reset()

        max_x_pos = 0
        ultima_x_pos = 0
        moedas = 0
        pontuacao = 0
        tempo_restante = 400
        venceu = False
        morreu = False
        info = {}
        gene_da_morte = 0
        gene_da_max_pos = 0
        frames_sem_progresso = 0
        max_frames_sem_progresso = 80

        for indice_gene, gene in enumerate(individuo.cromossomo):

            done = False
            terminated_aqui = False
            for _ in range(FRAME_SKIP):
                resultado = self.env.step(gene)

                if len(resultado) == 5:
                    obs, reward, terminated, truncated, info = resultado
                    done = terminated or truncated
                else:
                    obs, reward, done, info = resultado

                if self.renderizar:
                    try:
                        self.env.render()
                    except Exception:
                        pass

                if done or info.get('flag_get', False):
                    terminated_aqui = True
                    break

            x_pos = info.get('x_pos', 0)
            if x_pos > max_x_pos:
                max_x_pos = x_pos
                gene_da_max_pos = indice_gene
                frames_sem_progresso = 0
            else:
                frames_sem_progresso += 1
            ultima_x_pos = x_pos
            gene_da_morte = indice_gene

            moedas = info.get('coins', 0)
            pontuacao = info.get('score', 0)
            tempo_restante = info.get('time', 0)

            if info.get('flag_get', False):
                venceu = True
                break

            if done:
                if info.get('life', 2) < 2:
                    morreu = True
                break

            if frames_sem_progresso > max_frames_sem_progresso:
                break

        individuo.distancia_percorrida = max_x_pos
        individuo.venceu = venceu
        individuo.morreu = morreu
        individuo.moedas = moedas
        individuo.pontuacao = pontuacao
        individuo.tempo_restante = tempo_restante
        individuo.gene_da_morte = gene_da_morte
        individuo.gene_da_max_pos = gene_da_max_pos
        individuo.fitness = self._calcular_fitness(individuo)

        return individuo

    def _calcular_fitness(self, individuo):

        fitness = 0.0

        fitness += individuo.distancia_percorrida * PESO_DISTANCIA

        if individuo.distancia_percorrida > 100:
            fitness += individuo.tempo_restante * PESO_TEMPO

        fitness += individuo.moedas * PESO_MOEDAS

        fitness += individuo.pontuacao * PESO_PONTUACAO

        if individuo.venceu:
            fitness += BONUS_VITORIA

        if individuo.morreu:
            fitness += PENALIDADE_MORTE

        return max(fitness, 1.0)

    def fechar(self):
        if self.env is not None:
            try:
                self.env.close()
            except Exception:
                pass
            self.env = None