import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import PASTA_RESULTADOS, ARQUIVO_HISTORICO

class Estatisticas:

    def __init__(self, historico=None, melhor_global=None):

        self.historico = historico or []
        self.melhor_global = melhor_global

    def carregar_do_arquivo(self):

        if not os.path.exists(ARQUIVO_HISTORICO):
            print(f"Arquivo {ARQUIVO_HISTORICO} não encontrado.")
            return False

        self.historico = []
        with open(ARQUIVO_HISTORICO, 'r') as f:
            linhas = f.readlines()

        for linha in linhas[1:]:
            partes = linha.strip().split(';')
            if len(partes) < 5:
                continue
            self.historico.append({
                'geracao': int(partes[0]),
                'fitness_melhor': float(partes[1]),
                'fitness_media': float(partes[2]),
                'distancia_melhor': int(partes[3]),
                'venceu': partes[4].strip().lower() == 'true',
            })
        return True

    def gerar_relatorio(self):

        if not self.historico:
            print("Sem histórico para gerar relatório.")
            return

        total_geracoes = len(self.historico)
        primeira = self.historico[0]
        ultima = self.historico[-1]

        melhor_geracao = max(self.historico, key=lambda h: h['fitness_melhor'])

        geracao_vitoria = None
        for h in self.historico:
            if h['venceu']:
                geracao_vitoria = h['geracao']
                break

        if primeira['distancia_melhor'] > 0:
            evolucao_pct = (
                (ultima['distancia_melhor'] - primeira['distancia_melhor'])
                / primeira['distancia_melhor'] * 100
            )
        else:
            evolucao_pct = 0.0

        relatorio = []
        relatorio.append("=" * 70)
        relatorio.append("        RELATÓRIO FINAL - ALGORITMO GENÉTICO MARIO")
        relatorio.append("=" * 70)
        relatorio.append("")
        relatorio.append(f"Total de gerações executadas: {total_geracoes}")
        relatorio.append("")
        relatorio.append("--- PRIMEIRA GERAÇÃO ---")
        relatorio.append(f"  Melhor fitness:  {primeira['fitness_melhor']:.2f}")
        relatorio.append(f"  Fitness média:   {primeira['fitness_media']:.2f}")
        relatorio.append(f"  Maior distância: {primeira['distancia_melhor']} pixels")
        relatorio.append("")
        relatorio.append("--- ÚLTIMA GERAÇÃO ---")
        relatorio.append(f"  Melhor fitness:  {ultima['fitness_melhor']:.2f}")
        relatorio.append(f"  Fitness média:   {ultima['fitness_media']:.2f}")
        relatorio.append(f"  Maior distância: {ultima['distancia_melhor']} pixels")
        relatorio.append("")
        relatorio.append("--- MELHOR GERAÇÃO DA EVOLUÇÃO ---")
        relatorio.append(f"  Geração:         {melhor_geracao['geracao']}")
        relatorio.append(f"  Fitness:         {melhor_geracao['fitness_melhor']:.2f}")
        relatorio.append(f"  Distância:       {melhor_geracao['distancia_melhor']} pixels")
        relatorio.append("")
        relatorio.append("--- PROGRESSO GERAL ---")
        relatorio.append(f"  Evolução em distância: {evolucao_pct:+.1f}%")
        relatorio.append(f"  Mario venceu a fase?   {'SIM' if geracao_vitoria else 'NÃO'}")
        if geracao_vitoria:
            relatorio.append(f"  Geração da primeira vitória: {geracao_vitoria}")
        relatorio.append("")

        if self.melhor_global is not None:
            relatorio.append("--- MELHOR INDIVÍDUO GLOBAL ---")
            relatorio.append(f"  Fitness:    {self.melhor_global.fitness:.2f}")
            relatorio.append(f"  Distância:  {self.melhor_global.distancia_percorrida} pixels")
            relatorio.append(f"  Moedas:     {self.melhor_global.moedas}")
            relatorio.append(f"  Pontuação:  {self.melhor_global.pontuacao}")
            relatorio.append(f"  Venceu:     {'SIM' if self.melhor_global.venceu else 'NÃO'}")
            relatorio.append("")

        relatorio.append("=" * 70)

        texto = '\n'.join(relatorio)

        print('\n' + texto)

        caminho = os.path.join(PASTA_RESULTADOS, 'relatorio_final.txt')
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(texto)
        print(f"\nRelatório salvo em: {caminho}")

    def gerar_grafico_fitness(self):

        if not self.historico:
            print("Sem histórico para gerar gráfico.")
            return

        geracoes = [h['geracao'] for h in self.historico]
        fitness_melhor = [h['fitness_melhor'] for h in self.historico]
        fitness_media = [h['fitness_media'] for h in self.historico]

        plt.figure(figsize=(12, 6))
        plt.plot(geracoes, fitness_melhor, 'b-', linewidth=2,
                 label='Melhor Fitness', marker='o', markersize=4)
        plt.plot(geracoes, fitness_media, 'r--', linewidth=1.5,
                 label='Fitness Média', alpha=0.7)
        plt.fill_between(geracoes, fitness_media, fitness_melhor,
                         alpha=0.1, color='blue')
        plt.title('Evolução do Fitness ao Longo das Gerações', fontsize=14, fontweight='bold')
        plt.xlabel('Geração', fontsize=12)
        plt.ylabel('Fitness', fontsize=12)
        plt.legend(loc='best', fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        caminho = os.path.join(PASTA_RESULTADOS, 'grafico_fitness.png')
        plt.savefig(caminho, dpi=100)
        plt.close()
        print(f"Gráfico de fitness salvo em: {caminho}")

    def gerar_grafico_distancia(self):

        if not self.historico:
            return

        geracoes = [h['geracao'] for h in self.historico]
        distancias = [h['distancia_melhor'] for h in self.historico]

        meta_fase = 3160

        plt.figure(figsize=(12, 6))
        plt.plot(geracoes, distancias, 'g-', linewidth=2,
                 label='Maior Distância', marker='s', markersize=4)
        plt.axhline(y=meta_fase, color='red', linestyle='--',
                    linewidth=2, label=f'Fim da Fase ({meta_fase} pixels)')
        plt.fill_between(geracoes, 0, distancias, alpha=0.2, color='green')

        for h in self.historico:
            if h['venceu']:
                plt.axvline(x=h['geracao'], color='gold', alpha=0.5,
                            linestyle=':', linewidth=1)

        plt.title('Evolução da Distância Percorrida pelo Mario',
                  fontsize=14, fontweight='bold')
        plt.xlabel('Geração', fontsize=12)
        plt.ylabel('Distância (pixels)', fontsize=12)
        plt.legend(loc='best', fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        caminho = os.path.join(PASTA_RESULTADOS, 'grafico_distancia.png')
        plt.savefig(caminho, dpi=100)
        plt.close()
        print(f"Gráfico de distância salvo em: {caminho}")

    def gerar_grafico_combinado(self):

        if not self.historico:
            return

        geracoes = [h['geracao'] for h in self.historico]
        fitness_melhor = [h['fitness_melhor'] for h in self.historico]
        fitness_media = [h['fitness_media'] for h in self.historico]
        distancias = [h['distancia_melhor'] for h in self.historico]
        meta_fase = 3160
        progresso_pct = [min(d / meta_fase * 100, 100) for d in distancias]

        fig, axes = plt.subplots(3, 1, figsize=(12, 12))

        axes[0].plot(geracoes, fitness_melhor, 'b-', linewidth=2,
                     label='Melhor', marker='o', markersize=4)
        axes[0].plot(geracoes, fitness_media, 'r--', linewidth=1.5,
                     label='Média', alpha=0.7)
        axes[0].set_title('Evolução do Fitness', fontweight='bold')
        axes[0].set_xlabel('Geração')
        axes[0].set_ylabel('Fitness')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        axes[1].plot(geracoes, distancias, 'g-', linewidth=2,
                     marker='s', markersize=4)
        axes[1].axhline(y=meta_fase, color='red', linestyle='--',
                        linewidth=2, label=f'Fim da Fase ({meta_fase})')
        axes[1].fill_between(geracoes, 0, distancias, alpha=0.2, color='green')
        axes[1].set_title('Distância Percorrida (pixels)', fontweight='bold')
        axes[1].set_xlabel('Geração')
        axes[1].set_ylabel('Distância')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        axes[2].plot(geracoes, progresso_pct, color='purple', linewidth=2,
                     marker='^', markersize=4)
        axes[2].fill_between(geracoes, 0, progresso_pct, alpha=0.2, color='purple')
        axes[2].axhline(y=100, color='gold', linestyle='--',
                        linewidth=2, label='100% (fase completa)')
        axes[2].set_title('Progresso Percentual da Fase', fontweight='bold')
        axes[2].set_xlabel('Geração')
        axes[2].set_ylabel('Progresso (%)')
        axes[2].set_ylim(0, 110)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        plt.suptitle('Algoritmo Genético - Super Mario Bros',
                     fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()

        caminho = os.path.join(PASTA_RESULTADOS, 'grafico_completo.png')
        plt.savefig(caminho, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"Gráfico completo salvo em: {caminho}")

    def gerar_tudo(self):
        os.makedirs(PASTA_RESULTADOS, exist_ok=True)
        self.gerar_relatorio()
        self.gerar_grafico_fitness()
        self.gerar_grafico_distancia()
        self.gerar_grafico_combinado()
        print("\n✓ Estatísticas geradas com sucesso!")
        print(f"✓ Confira os arquivos na pasta '{PASTA_RESULTADOS}/'")

if __name__ == '__main__':

    print("Gerando relatório e gráficos a partir do histórico salvo...")
    stats = Estatisticas()

    try:
        import pickle
        from config import ARQUIVO_CHECKPOINT
        if os.path.exists(ARQUIVO_CHECKPOINT):
            with open(ARQUIVO_CHECKPOINT, 'rb') as f:
                estado = pickle.load(f)
            stats.melhor_global = estado.get('melhor_global')
            stats.historico = estado.get('historico', [])
    except Exception as e:
        print(f"Aviso: não foi possível carregar checkpoint ({e}).")
        stats.carregar_do_arquivo()

    if not stats.historico:
        stats.carregar_do_arquivo()

    if stats.historico:
        stats.gerar_tudo()
    else:
        print("Nenhum dado disponível ainda. Rode o programa primeiro.")
