from app import create_app
from app.extensions import db
from app.models import Veicolo, Fornitore, Manutenzione, Scadenza, User
from datetime import date
import os
import sqlite3

def add_missing_columns():
    """Aggiunge colonne mancanti al database esistente"""
    # Trova il database
    db_paths = ['instance/matrix_fleet.db', 'matrix_fleet.db', 'fleet_manager.db']
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("⚠️  Database non trovato")
        return
    
    print(f"📋 Aggiornamento database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista di colonne da aggiungere
        new_columns = [
            # VEICOLI
            ("veicoli", "carburante_personalizzato", "VARCHAR(50)"),
            ("veicoli", "carta_carburante", "VARCHAR(100)"),
            ("veicoli", "pin_carburante", "VARCHAR(20)"),
            ("veicoli", "societa_noleggio_id", "INTEGER"),
            ("veicoli", "nucleo", "VARCHAR(50) DEFAULT 'Via Capitel'"),
            
            # FORNITORI
            ("fornitori", "telefono_2", "VARCHAR(20)"),
            ("fornitori", "telefono_3", "VARCHAR(20)"),
            ("fornitori", "email_2", "VARCHAR(100)"),
            ("fornitori", "email_3", "VARCHAR(100)"),
            ("fornitori", "settore_2", "VARCHAR(50)"),
            ("fornitori", "settore_3", "VARCHAR(50)"),
            ("fornitori", "settore_personalizzato", "VARCHAR(100)"),
            ("fornitori", "nucleo", "VARCHAR(50) DEFAULT 'Via Capitel'"),
            
            # MANUTENZIONI
            ("manutenzioni", "nucleo", "VARCHAR(50) DEFAULT 'Via Capitel'"),
            
            # SCADENZE
            ("scadenze", "nucleo", "VARCHAR(50) DEFAULT 'Via Capitel'"),
        ]
        
        for table, column, column_type in new_columns:
            try:
                # Controlla se la colonna esiste
                cursor.execute(f"PRAGMA table_info({table})")
                existing_columns = [col[1] for col in cursor.fetchall()]
                
                if column not in existing_columns:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
                    print(f"  ✅ Aggiunta colonna {table}.{column}")
                else:
                    print(f"  ⚠️  Colonna {table}.{column} già presente")
                    
            except Exception as e:
                print(f"  ❌ Errore aggiunta {table}.{column}: {e}")
        
        # Crea tabella users se non esiste
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(120) NOT NULL,
                nucleo VARCHAR(50) DEFAULT 'Via Capitel',
                attivo BOOLEAN DEFAULT 1,
                data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_accesso DATETIME
            )
        """)
        print("  ✅ Tabella users verificata/creata")
        
        # Imposta nucleo predefinito per dati esistenti
        cursor.execute("UPDATE veicoli SET nucleo = 'Via Capitel' WHERE nucleo IS NULL")
        cursor.execute("UPDATE fornitori SET nucleo = 'Via Capitel' WHERE nucleo IS NULL")
        cursor.execute("UPDATE manutenzioni SET nucleo = 'Via Capitel' WHERE nucleo IS NULL")
        cursor.execute("UPDATE scadenze SET nucleo = 'Via Capitel' WHERE nucleo IS NULL")
        
        conn.commit()
        conn.close()
        
        print("🎉 Aggiornamento database completato!")
        
    except Exception as e:
        print(f"❌ Errore aggiornamento database: {e}")

app = create_app()

with app.app_context():
    # CONTROLLA SE IL DATABASE ESISTE GIÀ
    db_paths = ['instance/matrix_fleet.db', 'matrix_fleet.db', 'fleet_manager.db']
    db_exists = any(os.path.exists(path) for path in db_paths)
    
    if db_exists:
        print("📋 Database esistente trovato!")
        print("🔄 Aggiornamento struttura database...")
        
        # Aggiorna il database esistente
        add_missing_columns()
        
        # Crea solo tabelle mancanti (non sovrascrive)
        db.create_all()
        
        # CONTROLLA SE ESISTE L'UTENTE ADMIN (SENZA SOVRASCRIVERE PASSWORD!)
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            print("  ✅ Utente admin trovato - password mantenuta")
        else:
            # Crea utente admin SOLO se non esiste
            admin = User(
                username='admin',
                nucleo='Via Capitel',
                attivo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("  ✅ Utente admin creato con password predefinita")
        
        # Verifica se ci sono già dati
        veicoli_count = Veicolo.query.count()
        fornitori_count = Fornitore.query.count()
        manutenzioni_count = Manutenzione.query.count()
        scadenze_count = Scadenza.query.count()
        
        print(f"\n📊 Stato database aggiornato:")
        print(f"   - Veicoli: {veicoli_count}")
        print(f"   - Fornitori: {fornitori_count}")
        print(f"   - Manutenzioni: {manutenzioni_count}")
        print(f"   - Scadenze: {scadenze_count}")
        
        print("\n✅ Database aggiornato con successo!")
        print("🆕 Funzionalità disponibili:")
        print("   - 🔐 Sistema login sicuro con Flask-Login")
        print("   - 🛡️  Password con hash Werkzeug")
        print("   - 👤 Gestione sessioni utente")
        print("   - 🚪 Logout automatico")
        print("   - 🔒 Protezione route con @login_required")
        print("   - 🔑 Cambio password (password personalizzate vengono mantenute)")
        
    else:
        print("🆕 Primo avvio - Creazione nuovo database...")
        db.create_all()
        
        print("📊 Tabelle create:")
        print("   - Veicoli")
        print("   - Fornitori") 
        print("   - Manutenzioni")
        print("   - Scadenze")
        print("   - Users")
        
        # INSERISCI DATI DI ESEMPIO SOLO SE DATABASE VUOTO
        print("\n🔄 Inserimento dati di esempio...")
        
        # Fornitori di esempio
        fornitore1 = Fornitore(
            ragione_sociale="Officina Matrix Auto",
            partita_iva="12345678901",
            citta="Verona",
            cap="37100",
            provincia="VR",
            telefono="045-123456",
            email="info@matrixauto.it",
            settore="Officina",
            nucleo="Via Capitel"
        )
        
        fornitore2 = Fornitore(
            ragione_sociale="Gommista Neo",
            partita_iva="98765432109", 
            citta="Villafranca di Verona",
            cap="37069",
            provincia="VR",
            telefono="045-987654",
            settore="Gommista",
            nucleo="Via Capitel"
        )
        
        # Società di noleggio esempio
        fornitore3 = Fornitore(
            ragione_sociale="LEASYS Rent",
            partita_iva="11122233344",
            citta="Milano",
            cap="20100",
            provincia="MI",
            telefono="02-123456",
            email="info@leasys.com",
            settore="Società noleggio",
            nucleo="Via Capitel"
        )
        
        db.session.add(fornitore1)
        db.session.add(fornitore2)
        db.session.add(fornitore3)
        
        # Veicoli di esempio
        veicolo1 = Veicolo(
            targa="AB123CD",
            marca="Toyota",
            modello="Prius",
            anno_immatricolazione=2020,
            data_immatricolazione=date(2020, 3, 15),
            km_attuali=45000,
            carburante="Ibrido",
            cilindrata=1800,
            colore="Bianco",
            nucleo="Via Capitel"
        )
        
        veicolo2 = Veicolo(
            targa="EF456GH",
            marca="Volkswagen", 
            modello="Golf",
            anno_immatricolazione=2019,
            data_immatricolazione=date(2019, 6, 20),
            km_attuali=68000,
            carburante="Diesel",
            cilindrata=2000,
            colore="Grigio",
            carta_carburante="1234-5678-9012-3456",
            pin_carburante="1234",
            societa_noleggio_id=3,  # LEASYS
            nucleo="Via Capitel"
        )
        
        db.session.add(veicolo1)
        db.session.add(veicolo2)
        
        # Utente admin con password sicura (SOLO AL PRIMO AVVIO)
        admin = User(
            username="admin",
            nucleo="Via Capitel",
            attivo=True
        )
        admin.set_password("admin123")  # Password predefinita solo alla creazione
        db.session.add(admin)
        
        try:
            db.session.commit()
            print("✅ Dati di esempio inseriti!")
            print("🚗 2 veicoli aggiunti")
            print("🏢 3 fornitori aggiunti")
            print("👤 Utente admin creato")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Errore inserimento dati: {e}")
    
    print("\n🚀 Usa il file BAT per avviare l'applicazione!")
    print("🌐 Poi apri: http://localhost:5000")
    print("👤 Login: admin / password-corrente")
    print("🔐 Sistema login implementato con successo!")
