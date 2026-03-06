from fpdf import FPDF
from datetime import datetime
import os

class RapportPDF(FPDF):
    def header(self):
        # Gestion du logo
        if os.path.exists("./data/logoRTE.jpg"):
            self.image('./data/logoRTE.jpg', 10, 8, 33)
        
        self.set_font('Arial', 'B', 15)
        self.cell(40)
        self.cell(0, 10, clean_text("RAPPORT D'INCIDENT DE SÉCURITÉ"), 0, 1, 'C')
        
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(40)
        self.cell(0, 10, f'Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}', 0, 1, 'C')
        
        # --- AJOUT VISUEL URGENT ---
        # On vérifie si l'attribut 'is_urgent' a été passé à l'instance (on le fera via une variable globale ou un hack propre)
        # Pour faire simple ici, on gère l'urgence dans le corps du texte, 
        # mais si vous voulez un tampon en haut, il faut passer l'info au constructeur.
        # On va le gérer dans la fonction generer_pdf pour plus de simplicité.

        self.ln(10)
        self.set_draw_color(0, 51, 102)
        self.line(10, 35, 200, 35)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'RTE - Document Confidentiel - Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def clean_text(text):
    if text is None: return "Non renseigné"
    text = str(text).replace('€', 'Euros').replace('’', "'").replace('…', '...')
    try:
        return text.encode('latin-1', 'replace').decode('latin-1')
    except:
        return str(text)

def generer_pdf(data):
    pdf = RapportPDF('P', 'mm', 'A4')
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- TAMPON URGENT SI NÉCESSAIRE ---
    if data.get('urgent', False):
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(255, 0, 0) # ROUGE
        pdf.set_draw_color(255, 0, 0)
        # On dessine un cadre autour
        pdf.cell(0, 10, "!!! INCIDENT SIGNALÉ URGENT !!!", 1, 1, 'C')
        pdf.set_text_color(0) # Reset Noir
        pdf.set_draw_color(0) # Reset Noir
        pdf.ln(5)

    # ==========================================================
    # 1. CONTEXTE ET LOCALISATION
    # ==========================================================
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, clean_text("1. CONTEXTE ET LOCALISATION"), 0, 1, 'L', True)
    pdf.ln(2)
    
    # Date
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0)
    pdf.cell(40, 7, "Date du constat :", 0)
    pdf.set_font("Arial", 'B', 11)
    date_str = data['date'].strftime('%d/%m/%Y') if isinstance(data.get('date'), datetime) else str(data.get('date', 'N/A'))
    pdf.cell(0, 7, date_str, 0, 1)
    
    # Niveau d'urgence (Texte)
    pdf.set_font("Arial", '', 11)
    pdf.cell(40, 7, "Niveau d'urgence :", 0)
    pdf.set_font("Arial", 'B', 11)
    if data.get('urgent'):
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 7, "URGENT - Intervention requise", 0, 1)
    else:
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 7, "Standard", 0, 1)
    
    pdf.set_text_color(0)
    pdf.ln(2)

    # Bloc Gris Détails
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(100, 100, 100)
    pdf.cell(0, 7, clean_text("  Détails Géographiques"), 0, 1, 'L', True)
    pdf.set_text_color(0)
    
    def print_line(label, value):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 6, clean_text(label), 0)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, clean_text(value), 0, 1)

    if data.get('type') == 'site':
        print_line("Code Ouvrage (ID) :", data.get('id_ref'))
        print_line("Nom du Site :", data.get('label_complet', data.get('id_ref')))
        print_line("Commune :", f"{data.get('commune')} ({data.get('cp')})")
        print_line("Région / Dép :", f"{data.get('region')} / {data.get('departement')}")
        print_line("GMR / GDP :", f"{data.get('gmr')} / {data.get('gdp')}")
    else:
        print_line("Commune :", f"{data.get('commune')} ({data.get('cp')})")
        print_line("Département :", data.get('departement'))
        print_line("Région :", data.get('region'))
    
    pdf.ln(5)

    # ==========================================================
    # 2. DÉTAIL DES FAITS
    # ==========================================================
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 51, 102)
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(0, 10, clean_text("2. DÉTAIL DES FAITS CONSTATÉS"), 0, 1, 'L', True)
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(100, 100, 100)
    pdf.cell(60, 8, clean_text("Type d'acte"), 1, 0, 'C', True)
    pdf.cell(60, 8, clean_text("Catégorie Cible"), 1, 0, 'C', True)
    pdf.cell(70, 8, clean_text("Objet Spécifique"), 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(0)
    
    liste_faits = data.get('liste_faits', [])
    if not liste_faits and data.get('acte'):
        liste_faits = [{"acte": data.get('acte'), "categorie": data.get('cat_cible', ''), "objet": data.get('cible_spec', '')}]

    for fait in liste_faits:
        acte = clean_text(fait.get('acte',''))
        cat = clean_text(fait.get('categorie',''))
        obj = clean_text(fait.get('objet',''))
        
        pdf.cell(60, 8, acte, 1)
        pdf.cell(60, 8, cat, 1)
        pdf.cell(70, 8, obj, 1)
        pdf.ln()
    
    pdf.ln(5)

    # ==========================================================
    # 3. CONSTATATIONS TECHNIQUES
    # ==========================================================
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 51, 102)
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(0, 10, clean_text("3. CONSTATATIONS TECHNIQUES"), 0, 1, 'L', True)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(0)
    col_gauche = 50
    h_ligne = 7
    
    raw_obstacles = data.get('obstacles_list', [])
    if isinstance(raw_obstacles, list) and len(raw_obstacles) > 0:
        obstacle_str = ", ".join(raw_obstacles)
    else:
        obstacle_str = str(data.get('obstacle', 'Aucun'))
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(col_gauche, h_ligne, clean_text("Système SIV déclenché :"), 0)
    siv_val = clean_text(str(data.get('siv', 'Non')))
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, h_ligne, siv_val, 0, 1)

    print_line("Mesures conservatoires :", data.get('mesure_provisoire', 'Aucune'))
    
    pdf.ln(3)
    pdf.set_font("Arial", 'B', 10)
    pdf.write(6, clean_text("Description détaillée des faits :\n"))
    pdf.set_font("Arial", '', 10)
    pdf.set_fill_color(255, 255, 240) 
    desc = data.get('desc') if data.get('desc') else "Aucune description complémentaire saisie."
    pdf.multi_cell(0, 6, clean_text(desc), 1, 'L', True)
    pdf.ln(5)

    # ==========================================================
    # 4. IMPACT ET SUIVI
    # ==========================================================
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 51, 102)
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(0, 10, clean_text("4. IMPACT ET SUIVI"), 0, 1, 'L', True)
    pdf.ln(2)
    pdf.set_text_color(0)
    
    cout_val = str(data.get('cout', '0'))
    print_line("Préjudice estimé :", f"{cout_val} k Euros")
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(col_gauche, h_ligne, clean_text("Statut de la plainte :"), 0)
    plainte_val = clean_text(data.get('plainte', 'Non renseigné'))
    
    if "Déposée" in plainte_val or "prévu" in plainte_val.lower():
        pdf.set_text_color(0, 0, 200)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, h_ligne, plainte_val, 0, 1)
    pdf.set_text_color(0) 

    if data.get('chemin_fichier'):
        pdf.ln(5)
        pdf.set_font("Arial", 'I', 9)
        pdf.set_text_color(100, 100, 100)
        nom_fichier = os.path.basename(data.get('chemin_fichier'))
        pdf.cell(0, h_ligne, clean_text(f"[Pièce jointe associée : {nom_fichier}]"), 0, 1)

    return bytes(pdf.output(dest='S'))