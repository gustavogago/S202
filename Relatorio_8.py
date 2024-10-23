from neo4j import GraphDatabase

class GameDatabase:
    def __init__(self, uri, user, password):
        """
        Inicializa a conexão com o banco de dados Neo4j.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        self.driver.close()
    
    # Métodos para Jogadores
    def create_player(self, player_id, name):
        """
        Cria um novo jogador ou atualiza o nome se o jogador já existir.
        """
        with self.driver.session() as session:
            result = session.run(
                "MERGE (p:Player {player_id: $player_id}) "
                "SET p.name = $name "
                "RETURN p",
                player_id=player_id,
                name=name
            )
            record = result.single()
            if record:
                return dict(record['p'])
            else:
                return None

    def update_player(self, player_id, name):
        """
        Atualiza o nome de um jogador existente.
        """
        with self.driver.session() as session:
            result = session.run(
                "MATCH (p:Player {player_id: $player_id}) "
                "SET p.name = $name "
                "RETURN p",
                player_id=player_id,
                name=name
            )
            record = result.single()
            if record:
                return dict(record['p'])
            else:
                return None

    def delete_player(self, player_id):
        """
        Exclui um jogador e todas as suas relações.
        """
        with self.driver.session() as session:
            session.run(
                "MATCH (p:Player {player_id: $player_id}) "
                "DETACH DELETE p",
                player_id=player_id
            )

    def get_player(self, player_id):
        """
        Recupera as informações de um jogador específico.
        """
        with self.driver.session() as session:
            result = session.run(
                "MATCH (p:Player {player_id: $player_id}) "
                "RETURN p",
                player_id=player_id
            )
            record = result.single()
            if record:
                return dict(record['p'])
            else:
                return None

    def list_players(self):
        """
        Retorna uma lista de todos os jogadores.
        """
        with self.driver.session() as session:
            result = session.run(
                "MATCH (p:Player) "
                "RETURN p"
            )
            return [dict(record['p']) for record in result]

    # Métodos para Partidas
    def create_match(self, match_id, players, result):
        """
        Cria uma nova partida, relaciona os jogadores e registra os resultados.
        """
        with self.driver.session() as session:
            # Cria o nó da partida
            session.run(
                "MERGE (m:Match {match_id: $match_id})",
                match_id=match_id
            )
            # Cria relações entre jogadores e partida com os resultados
            for player_id in players:
                score = result.get(player_id)
                session.run(
                    "MATCH (p:Player {player_id: $player_id}), (m:Match {match_id: $match_id}) "
                    "MERGE (p)-[r:PLAYED_IN]->(m) "
                    "SET r.score = $score",
                    player_id=player_id,
                    match_id=match_id,
                    score=score
                )

    def update_match(self, match_id, players, result):
        """
        Atualiza uma partida existente com novos jogadores e resultados.
        """
        with self.driver.session() as session:
            # Remove relações existentes
            session.run(
                "MATCH (p:Player)-[r:PLAYED_IN]->(m:Match {match_id: $match_id}) "
                "DELETE r",
                match_id=match_id
            )
            # Recria relações com jogadores e resultados atualizados
            for player_id in players:
                score = result.get(player_id)
                session.run(
                    "MATCH (p:Player {player_id: $player_id}), (m:Match {match_id: $match_id}) "
                    "CREATE (p)-[r:PLAYED_IN {score: $score}]->(m)",
                    player_id=player_id,
                    match_id=match_id,
                    score=score
                )

    def delete_match(self, match_id):
        """
        Exclui uma partida e todas as suas relações.
        """
        with self.driver.session() as session:
            session.run(
                "MATCH (m:Match {match_id: $match_id}) "
                "DETACH DELETE m",
                match_id=match_id
            )

    def get_match(self, match_id):
        """
        Recupera as informações de uma partida específica, incluindo jogadores e resultados.
        """
        with self.driver.session() as session:
            result = session.run(
                "MATCH (m:Match {match_id: $match_id}) "
                "OPTIONAL MATCH (p:Player)-[r:PLAYED_IN]->(m) "
                "RETURN m, collect({player: p, score: r.score}) as players",
                match_id=match_id
            )
            record = result.single()
            if record and record['m']:
                match_info = {
                    'match': dict(record['m']),
                    'players': [
                        {'player': dict(player['player']), 'score': player['score']}
                        for player in record['players']
                    ]
                }
                return match_info
            else:
                return None

    def get_player_match_history(self, player_id):
        """
        Obtém o histórico de partidas de um jogador.
        """
        with self.driver.session() as session:
            result = session.run(
                "MATCH (p:Player {player_id: $player_id})-[r:PLAYED_IN]->(m:Match) "
                "RETURN m, r.score ORDER BY m.match_id",
                player_id=player_id
            )
            history = []
            for record in result:
                match = dict(record['m'])
                score = record['r.score']
                history.append({
                    'match': match,
                    'score': score
                })
            return history

    def record_match_result(self, match_id, players, result):
        """
        Registra ou atualiza os resultados de uma partida entre jogadores.
        """
        with self.driver.session() as session:
            for player_id in players:
                score = result.get(player_id)
                session.run(
                    "MATCH (p:Player {player_id: $player_id}), (m:Match {match_id: $match_id}) "
                    "MERGE (p)-[r:PLAYED_IN]->(m) "
                    "SET r.score = $score",
                    player_id=player_id,
                    match_id=match_id,
                    score=score
                )

db = GameDatabase("bolt://localhost:7687", "neo4j", "abcdefgh")

# Criar jogadores
db.create_player("player1", "Alice")
db.create_player("player2", "Bob")

# Criar uma partida e registrar resultados
players = ["player1", "player2"]
results = {"player1": 10, "player2": 8}
db.create_match("match1", players, results)

# Obter lista de jogadores
players_list = db.list_players()
print("Lista de Jogadores:")
for player in players_list:
    print(player)

# Obter informações de uma partida específica
match_info = db.get_match("match1")
print("\nInformações da Partida:")
print(match_info)

# Obter histórico de partidas de um jogador
history = db.get_player_match_history("player1")
print("\nHistórico de Partidas de Alice:")
for h in history:
    print(h)

# Fechar a conexão
db.close()
