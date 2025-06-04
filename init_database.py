from backend.database import Database

def main():
    """
    Inicializa o banco de dados e popula com dados dos arquivos de texto.
    """
    print("Inicializando banco de dados...")
    db = Database()
    
    print("Criando tabelas...")
    db.create_tables()
    
    print("Populando banco de dados com dados dos arquivos de texto...")
    db.populate_from_files()
    
    print("Banco de dados inicializado com sucesso!")
    db.close()

if __name__ == "__main__":
    main()