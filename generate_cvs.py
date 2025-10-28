"""
Script pour générer 250 CV en PDF
"""
import random
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
from datetime import datetime, timedelta
import json

# Initialiser Faker en français
fake = Faker('fr_FR')
Faker.seed(42)
random.seed(42)

# Répertoire de sortie
OUTPUT_DIR = Path("data/pdf_cv")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Définir les métiers et leurs ratios (pour 250 CV, puis multiplier par 10)
JOBS = {
    # Développeurs (70%)
    "Développeur Python": 15,
    "Développeur Java": 12,
    "Développeur JavaScript": 10,
    "Développeur React": 8,
    "Développeur Angular": 8,
    "Développeur Vue.js": 6,
    "Développeur PHP": 6,
    "Développeur .NET": 6,
    "Développeur Full Stack": 8,
    "Développeur Backend": 5,
    
    # Product Owners (10%)
    "Product Owner": 10,
    
    # RH et recrutement (8%)
    "Responsable RH": 5,
    "Chargé de Recrutement": 3,
    
    # Autres (12%)
    "Scrum Master": 4,
    "DevOps Engineer": 4,
    "Chef de Projet": 4,
}

# Hobbies
HOBBIES = [
    "Photographie",
    "Randonnée et montagne",
    "Musique (guitare/piano)",
    "Voyage et découverte",
    "Course à pied",
    "Cuisine et pâtisserie",
    "Lecture (sciences-tech)",
    "Cyclisme",
    "Natation",
    "Tennis",
    "Bénévolat dans des associations",
    "Jeux vidéo stratégiques",
    "Yoga et méditation",
    "Cinéma et séries",
    "Sport collectif (football, basket)",
    "Nouvelles technologies",
    "Blogging tech",
    "Open source contributions",
]

# Travaux associatifs
ASSOCIATIVE_WORK = [
    "Bénévole - Association d'aide aux étudiants en informatique",
    "Membre actif - Association Tech pour l'éducation",
    "Bénévole - Organisation d'événements tech locaux",
    "Mentor - Programme de mentorat junior developers",
    "Bénévole - Initiation au code pour enfants",
    "Membre - Association de sensibilisation aux femmes dans le tech",
    "Bénévole - Aide aux personnes âgées avec le numérique",
    "Organisateur - Meetups et conférences tech",
    "Bénévole - Recyclage et environnement",
    "Membre - Association humanitaire",
    "Bénévole - Organisation de hackathons",
    "Membre actif - Association de quartier",
]

def get_technologies(job):
    """Retourne les technologies appropriées selon le métier"""
    tech_map = {
        "Développeur Python": ["Python", "Django", "Flask", "FastAPI", "PostgreSQL", "MongoDB"],
        "Développeur Java": ["Java", "Spring Boot", "Hibernate", "MySQL", "Maven", "JUnit"],
        "Développeur JavaScript": ["JavaScript", "Node.js", "Express", "React", "Webpack"],
        "Développeur React": ["React", "Redux", "TypeScript", "Webpack", "Jest", "Git"],
        "Développeur Angular": ["Angular", "TypeScript", "RxJS", "NgRx", "Node.js"],
        "Développeur Vue.js": ["Vue.js", "Vuex", "Vue Router", "TypeScript", "Webpack"],
        "Développeur PHP": ["PHP", "Symfony", "Laravel", "MySQL", "Composer"],
        "Développeur .NET": [".NET", "C#", "ASP.NET", "SQL Server", "Entity Framework"],
        "Développeur Full Stack": ["JavaScript", "React", "Node.js", "Python", "PostgreSQL", "Docker"],
        "Développeur Backend": ["Node.js", "Python", "REST API", "PostgreSQL", "Redis", "AWS"],
        "Product Owner": ["Jira", "Confluence", "Scrum", "Product Management", "Agile"],
        "Scrum Master": ["Scrum", "Kanban", "Agile", "SAFe", "Jira", "Confluence"],
        "DevOps Engineer": ["Docker", "Kubernetes", "Jenkins", "CI/CD", "AWS", "Linux"],
        "Chef de Projet": ["Gestion de projet", "PMP", "Agile", "Prince2", "MS Project"],
    }
    return tech_map.get(job, ["Informatique", "Gestion"])

def get_competences(job):
    """Retourne les compétences appropriées"""
    comp_map = {
        "Responsable RH": ["Recrutement", "Gestion des talents", "Formation", "Droit du travail", "GPEC"],
        "Chargé de Recrutement": ["Sourcing", "Entretiens", "ATS", "LinkedIn", "Viadeo"],
    }
    return comp_map.get(job, [])

def generate_company():
    """Génère un nom d'entreprise"""
    company_types = ["Solutions", "Technologies", "Innovation", "Digital", "Systems", "Services", "Group"]
    prefixes = ["Tech", "Digital", "Global", "Advanced", "Smart", "Future", "Prime"]
    return f"{random.choice(prefixes)} {random.choice(company_types)}"

def generate_cv(job_title):
    """Génère un CV complet"""
    
    # Informations personnelles
    first_name = fake.first_name()
    last_name = fake.last_name()
    age = random.randint(25, 55)
    email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
    phone = fake.phone_number()
    
    # Adresse
    address = f"{fake.street_address()}, {fake.postcode()} {fake.city()}"
    
    # Expérience (3-6 postes)
    num_jobs = random.randint(3, 6)
    experiences = []
    current_date = datetime.now()
    
    # Compétences/Technologies
    if "Développeur" in job_title or "Engineer" in job_title:
        technologies = get_technologies(job_title)
        competences = technologies + random.sample([
            "Git", "Docker", "CI/CD", "TDD", "Clean Code", "Microservices",
            "REST API", "GraphQL", "AWS", "Azure", "Linux", "Shell"
        ], random.randint(3, 6))
    elif job_title in ["Product Owner", "Scrum Master"]:
        competences = get_technologies(job_title) + [
            "Stakeholder Management", "User Stories", "Sprint Planning"
        ]
    elif "RH" in job_title or "Recrutement" in job_title:
        competences = get_competences(job_title) + [
            "Communication", "Négociation", "Analyse comportementale"
        ]
    else:
        competences = get_technologies(job_title)
    
    # Générer les expériences
    for i in range(num_jobs):
        if i == 0:
            start_date = current_date - timedelta(days=random.randint(180, 730))
            end_date = None  # Poste actuel
            duration = "Aujourd'hui"
        else:
            end_date = current_date - timedelta(days=random.randint(i*730, (i+1)*730))
            start_date = end_date - timedelta(days=random.randint(365, 1460))
            months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            duration = f"{months} mois"
        
        exp = {
            "job": job_title if i == 0 else random.choice(list(JOBS.keys())),
            "company": generate_company(),
            "start": start_date.strftime("%m/%Y"),
            "end": "Aujourd'hui" if end_date is None else end_date.strftime("%m/%Y"),
            "duration": duration,
            "description": generate_job_description(job_title if i == 0 else random.choice(list(JOBS.keys())))
        }
        experiences.append(exp)
        current_date = end_date if end_date else start_date
    
    # Formation
    formations = [
        f"Master {job_title} - Université {fake.city()} ({random.randint(2010, 2020)})",
        f"Bac+5 en Informatique - École {fake.city()} ({random.randint(2008, 2018)})"
    ]
    
    # Hobbies (3-5 hobbies aléatoires)
    num_hobbies = random.randint(3, 5)
    hobbies = random.sample(HOBBIES, min(num_hobbies, len(HOBBIES)))
    
    # Travaux associatifs (1-2 activités)
    num_associative = random.randint(1, 2)
    associative_work = random.sample(ASSOCIATIVE_WORK, min(num_associative, len(ASSOCIATIVE_WORK)))
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "age": age,
        "email": email,
        "phone": phone,
        "address": address,
        "job_title": job_title,
        "competences": competences,
        "experiences": experiences,
        "formations": formations,
        "hobbies": hobbies,
        "associative_work": associative_work
    }

def generate_job_description(job_title):
    """Génère une description de poste"""
    descriptions = {
        "Développeur Python": [
            "Développement d'applications web avec Django et FastAPI",
            "Optimisation de bases de données PostgreSQL",
            "Mise en place de solutions de microservices"
        ],
        "Développeur Java": [
            "Développement d'applications Spring Boot",
            "Architecture microservices avec Java EE",
            "Intégration continue avec Jenkins et GitLab CI"
        ],
        "Développeur React": [
            "Développement d'interfaces utilisateur avec React",
            "Intégration d'APIs REST",
            "Optimisation des performances frontend"
        ],
        "Product Owner": [
            "Gestion du backlog produit",
            "Définition des user stories et critères d'acceptation",
            "Collaboration avec les équipes techniques et stakeholders"
        ],
        "Responsable RH": [
            "Recrutement et gestion des talents",
            "Développement de la politique RH",
            "Suivi de la formation et du développement des compétences"
        ],
        "Chargé de Recrutement": [
            "Sourcing de candidats sur LinkedIn et réseaux sociaux",
            "Conducting interviews et évaluation des compétences",
            "Suivi et reporting des KPIs de recrutement"
        ],
        "Scrum Master": [
            "Facilitation des cérémonies Scrum",
            "Coaching des équipes pour l'amélioration continue",
            "Suppression des obstacles et gestion des impediments"
        ],
        "DevOps Engineer": [
            "Mise en place de pipelines CI/CD",
            "Containerisation avec Docker et orchestration Kubernetes",
            "Monitoring et infrastructure cloud AWS/Azure"
        ],
    }
    
    # Retourner toute la liste des descriptions au lieu d'une seule
    desc = descriptions.get(job_title, ["Gestion de projet et coordination d'équipes"])
    return desc  # Retourner toute la liste

def create_pdf_cv(cv_data, output_path):
    """Crée un PDF de CV"""
    
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2E7D32'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1565C0'),
        spaceAfter=6
    )
    
    # Nom et titre
    name = f"{cv_data['first_name']} {cv_data['last_name']}"
    story.append(Paragraph(name, title_style))
    story.append(Paragraph(cv_data['job_title'], subtitle_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Informations personnelles
    info_data = [
        ['Email:', cv_data['email']],
        ['Téléphone:', cv_data['phone']],
        ['Adresse:', cv_data['address']]
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 4.5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Compétences
    story.append(Paragraph('<b>Compétences Techniques</b>', styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    # Organiser les compétences en colonnes
    competences_text = " • ".join(cv_data['competences'][:15])
    story.append(Paragraph(competences_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Expériences
    story.append(Paragraph('<b>Expérience Professionnelle</b>', styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    for exp in cv_data['experiences']:
        date_str = f"{exp['start']} - {exp['end']}"
        exp_title = f"<b>{exp['job']}</b> - {exp['company']}"
        exp_period = f"<i>{date_str} ({exp['duration']})</i>"
        
        story.append(Paragraph(exp_title, styles['Normal']))
        story.append(Paragraph(exp_period, styles['Normal']))
        
        # Description des tâches - regrouper en un seul texte
        tasks_text = "<br/>".join([f"• {task}" for task in exp['description']])
        story.append(Paragraph(tasks_text, styles['Normal']))
        
        story.append(Spacer(1, 0.15*inch))
    
    # Formation
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph('<b>Formation</b>', styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    formations_text = "<br/>".join([f"• {formation}" for formation in cv_data['formations']])
    story.append(Paragraph(formations_text, styles['Normal']))
    
    # Hobbies
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph('<b>Centres d\'intérêt</b>', styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    hobbies_text = ", ".join(cv_data['hobbies'])
    story.append(Paragraph(hobbies_text, styles['Normal']))
    
    # Travaux associatifs
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph('<b>Engagements associatifs</b>', styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    associative_text = "<br/>".join([f"• {work}" for work in cv_data['associative_work']])
    story.append(Paragraph(associative_text, styles['Normal']))
    
    # Générer le PDF
    doc.build(story)

def main():
    """Fonction principale"""
    print("Génération de 2500 CV en PDF...")
    print("="*60)
    
    # Créer la distribution des métiers pour 2500 CV
    jobs_list = []
    
    # Multiplier les ratios pour atteindre ~2500 CV
    multiplier = 10  # Pour avoir environ 2500 CV
    
    for job, count in JOBS.items():
        jobs_list.extend([job] * (count * multiplier))
    
    # S'assurer d'avoir exactement 2500 CV
    while len(jobs_list) < 2500:
        jobs_list.append(random.choice(list(JOBS.keys())))
    
    jobs_list = jobs_list[:2500]
    
    # Statistiques
    job_counts = {}
    for job in jobs_list:
        job_counts[job] = job_counts.get(job, 0) + 1
    
    print("\nDistribution des CV:")
    print("-" * 60)
    for job, count in sorted(job_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{job:.<40} {count:>3} CV")
    
    print(f"\n{'='*60}")
    print(f"Total: {len(jobs_list)} CV\n")
    
    # Générer les CV
    for i, job in enumerate(jobs_list, 1):
        print(f"Génération CV {i}/2500: {job}...", end=" ")
        
        cv_data = generate_cv(job)
        
        # Nom du fichier
        filename_base = f"CV_{cv_data['job_title']}_{cv_data['first_name']}_{cv_data['last_name']}"
        # Remplacer les espaces et points dans le nom mais garder l'extension .pdf
        filename_base = filename_base.replace(" ", "_").replace(".", "")
        filename = f"{filename_base}.pdf"
        output_path = OUTPUT_DIR / filename
        
        # Créer le PDF
        try:
            create_pdf_cv(cv_data, output_path)
            print(f"[OK] {filename}")
        except Exception as e:
            print(f"[ERREUR] {e}")
    
    print(f"\n{'='*60}")
    print(f"[OK] Generation terminee!")
    pdf_count = len(list(OUTPUT_DIR.glob('*.pdf')))
    print(f"[OK] {pdf_count} fichiers crees dans {OUTPUT_DIR}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

