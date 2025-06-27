from app import create_app
from app.extensions import db
from app.models import Veicolo, Fornitore, Manutenzione, Scadenza
from datetime import date
import os

app = create_app()

with app.app_context():
    # CONTROLLA SE IL DATABASE ESISTE GIÀ
    db_exists = os.path.exists('fleet_manager.db')
    
    if db_exists:
        print("⚠️  Database già esistente!")
        choice = input("Vuoi cancellare tutto e ricominciare? (y/N): ").lower().strip()
        
        if choice == 'y' or choice == 'yes':
            print("🗑️  Cancellazione database esistente...")
            db.drop_all()
            db.create_all()
            print("✅ Database ricreato!")
        else:
            print("✅ Database esistente mantenuto!")
            print("🔄 Creazione solo tabelle mancanti...")
            db.create_all()  # Crea solo le tabelle che non esistono
            
            # Verifica se ci sono già dati
            veicoli_count = Veicolo.query.count()
            fornitori_count = Fornitore.query.count()
            
            print(f"📊 Stato database:")
            print(f"   - Veicoli: {veicoli_count}")
            print(f"   - Fornitori: {fornitori_count}")
            
            if veicoli_count > 0 or fornitori_count > 0:
                print("ℹ️  Database contiene già dati. Non inserisco esempi.")
                print("🚀 Avvia l'applicazione con: python main.py")
                exit()
    else:
        print("🆕 Primo avvio - Creazione nuovo database...")
        db.create_all()
    
    print("📊 Tabelle create/verificate:")
    print("   - Veicoli")
    print("   - Fornitori") 
    print("   - Manutenzioni")
    print("   - Scadenze")
    
    # INSERISCI DATI DI ESEMPIO SOLO SE DATABASE VUOTO
    if Veicolo.query.count() == 0:
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
            settore="Officina"
        )
        
        fornitore2 = Fornitore(
            ragione_sociale="Gommista Neo",
            partita_iva="98765432109", 
            citta="Villafranca di Verona",
            cap="37069",
            provincia="VR",
            telefono="045-987654",
            settore="Gommista"
        )
        
        db.session.add(fornitore1)
        db.session.add(fornitore2)
        
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
            colore="Bianco"
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
            colore="Grigio"
        )
        
        db.session.add(veicolo1)
        db.session.add(veicolo2)
        
        try:
            db.session.commit()
            print("✅ Dati di esempio inseriti!")
            print("🚗 2 veicoli aggiunti")
            print("🏢 2 fornitori aggiunti")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Errore inserimento dati: {e}")
    else:
        print("ℹ️  Database già popolato - Non inserisco dati di esempio")
    
    print("\n🚀 Avvia l'applicazione con: python main.py")
    print("🌐 Poi apri: http://localhost:5000")
