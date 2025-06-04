import sqlite3
import os
import json

class Database:
    def __init__(self, db_path='data/prescriva.db'):
        """
        Inicializa a conexão com o banco de dados.
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self.conn = None
        self.create_tables()
    
    def connect(self):
        """
        Estabelece uma conexão com o banco de dados.
        
        Returns:
            sqlite3.Connection: Objeto de conexão com o banco de dados
        """
        if self.conn is None:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """
        Fecha a conexão com o banco de dados.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def create_tables(self):
        """
        Cria as tabelas necessárias no banco de dados.
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Tabela de medicamentos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            laboratorio TEXT,
            preco REAL,
            validade INTEGER,
            bula TEXT
        )
        ''')
        
        # Tabela de farmácias
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS farmacias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cidade TEXT NOT NULL,
            endereco TEXT NOT NULL,
            telefone TEXT,
            horario TEXT
        )
        ''')
        
        # Tabela de relação entre medicamentos e farmácias
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicamento_farmacia (
            medicamento_id INTEGER,
            farmacia_id INTEGER,
            PRIMARY KEY (medicamento_id, farmacia_id),
            FOREIGN KEY (medicamento_id) REFERENCES medicamentos (id),
            FOREIGN KEY (farmacia_id) REFERENCES farmacias (id)
        )
        ''')
        
        # Tabela de prescrições
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescricoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medico TEXT,
            paciente TEXT,
            data TEXT,
            medicamentos TEXT,
            observacoes TEXT,
            pdf_url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
    
    def populate_from_files(self):
        """
        Popula o banco de dados com informações dos arquivos de texto.
        """
        self.populate_medicamentos()
        self.populate_farmacias()
    
    def populate_medicamentos(self):
        """
        Popula a tabela de medicamentos a partir do arquivo medicamentos.txt.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Verificar se a tabela já está populada
            cursor.execute("SELECT COUNT(*) FROM medicamentos")
            if cursor.fetchone()[0] > 0:
                return
            
            with open('data/medicamentos.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Dividir o conteúdo por medicamentos
                medicamentos_raw = content.split('MEDICAMENTO: ')[1:]
                
                for med_raw in medicamentos_raw:
                    lines = med_raw.strip().split('\n')
                    nome = lines[0].strip()
                    
                    laboratorio = None
                    preco = None
                    validade = None
                    farmacias = []
                    bula = None
                    
                    for line in lines[1:]:
                        if line.startswith('LABORATÓRIO:'):
                            laboratorio = line.replace('LABORATÓRIO:', '').strip()
                        elif line.startswith('PREÇO:'):
                            preco_str = line.replace('PREÇO:', '').strip().replace('R$', '').strip()
                            preco = float(preco_str.replace(',', '.'))
                        elif line.startswith('VALIDADE:'):
                            validade_str = line.replace('VALIDADE:', '').strip().split()[0]
                            validade = int(validade_str)
                        elif line.startswith('FARMÁCIAS:'):
                            farmacias = [f.strip() for f in line.replace('FARMÁCIAS:', '').strip().split(',')]
                        elif line.startswith('BULA:'):
                            bula = line.replace('BULA:', '').strip()
                    
                    # Inserir medicamento
                    cursor.execute(
                        "INSERT INTO medicamentos (nome, laboratorio, preco, validade, bula) VALUES (?, ?, ?, ?, ?)",
                        (nome, laboratorio, preco, validade, bula)
                    )
                    medicamento_id = cursor.lastrowid
                    
                    # Relacionar com farmácias
                    for farmacia_nome in farmacias:
                        cursor.execute("SELECT id FROM farmacias WHERE nome = ?", (farmacia_nome,))
                        result = cursor.fetchone()
                        if result:
                            farmacia_id = result[0]
                            cursor.execute(
                                "INSERT OR IGNORE INTO medicamento_farmacia (medicamento_id, farmacia_id) VALUES (?, ?)",
                                (medicamento_id, farmacia_id)
                            )
            
            conn.commit()
        
        except Exception as e:
            print(f"Erro ao popular medicamentos: {e}")
    
    def populate_farmacias(self):
        """
        Popula a tabela de farmácias a partir do arquivo farmacias.txt.
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Verificar se a tabela já está populada
            cursor.execute("SELECT COUNT(*) FROM farmacias")
            if cursor.fetchone()[0] > 0:
                return
            
            with open('data/farmacias.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Dividir o conteúdo por farmácias
                farmacias_raw = content.split('FARMÁCIA: ')[1:]
                
                for farm_raw in farmacias_raw:
                    lines = farm_raw.strip().split('\n')
                    nome = lines[0].strip()
                    
                    cidade = None
                    enderecos = []
                    telefone = None
                    horario = None
                    
                    i = 1
                    while i < len(lines):
                        line = lines[i]
                        if line.startswith('CIDADE:'):
                            cidade = line.replace('CIDADE:', '').strip()
                        elif line.startswith('ENDEREÇOS:'):
                            i += 1
                            while i < len(lines) and lines[i].startswith('- '):
                                enderecos.append(lines[i].replace('- ', '').strip())
                                i += 1
                            continue
                        elif line.startswith('TELEFONE:'):
                            telefone = line.replace('TELEFONE:', '').strip()
                        elif line.startswith('HORÁRIO:'):
                            horario = line.replace('HORÁRIO:', '').strip()
                        i += 1
                    
                    # Inserir cada endereço como uma farmácia separada
                    for endereco in enderecos:
                        cursor.execute(
                            "INSERT INTO farmacias (nome, cidade, endereco, telefone, horario) VALUES (?, ?, ?, ?, ?)",
                            (nome, cidade, endereco, telefone, horario)
                        )
            
            conn.commit()
        
        except Exception as e:
            print(f"Erro ao popular farmácias: {e}")
    
    def save_prescription(self, prescription_data, pdf_url=None):
        """
        Salva uma prescrição no banco de dados.
        
        Args:
            prescription_data (dict): Dados da prescrição
            pdf_url (str): URL do PDF no S3
            
        Returns:
            int: ID da prescrição salva
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO prescricoes (medico, paciente, data, medicamentos, observacoes, pdf_url) VALUES (?, ?, ?, ?, ?, ?)",
            (
                prescription_data.get('medico'),
                prescription_data.get('paciente'),
                prescription_data.get('data'),
                json.dumps(prescription_data.get('medicamentos', []), ensure_ascii=False),
                prescription_data.get('observacoes'),
                pdf_url
            )
        )
        
        conn.commit()
        return cursor.lastrowid
    
    def get_medicamento_info(self, nome):
        """
        Obtém informações sobre um medicamento.
        
        Args:
            nome (str): Nome do medicamento
            
        Returns:
            dict: Informações do medicamento
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT m.*, GROUP_CONCAT(f.nome) as farmacias
            FROM medicamentos m
            LEFT JOIN medicamento_farmacia mf ON m.id = mf.medicamento_id
            LEFT JOIN farmacias f ON mf.farmacia_id = f.id
            WHERE m.nome LIKE ?
            GROUP BY m.id
            """,
            (f"%{nome}%",)
        )
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        return None
    
    def get_farmacias_by_medicamento(self, medicamento_nome):
        """
        Obtém as farmácias que vendem um determinado medicamento.
        
        Args:
            medicamento_nome (str): Nome do medicamento
            
        Returns:
            list: Lista de farmácias
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT f.*
            FROM farmacias f
            JOIN medicamento_farmacia mf ON f.id = mf.farmacia_id
            JOIN medicamentos m ON mf.medicamento_id = m.id
            WHERE m.nome LIKE ?
            """,
            (f"%{medicamento_nome}%",)
        )
        
        return [dict(row) for row in cursor.fetchall()]